# kva/__init__.py

import atexit
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from glob import glob
from tqdm import tqdm
from functools import lru_cache
from collections import defaultdict

import pandas as pd

from kva.utils import (storage_path, set_storage, CustomJSONEncoder, File, LogFile, Folder, Table,
                       _deep_merge, get_latest_nonnull, logger, KeyAwareDefaultDict)

git_semaphore = threading.Semaphore()


default_context = {
    'cwd': os.getcwd(),
    'cmd': ' '.join(os.sys.argv)
}


# Cache context data
@lru_cache
def cached_load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_jsonl(path):
    if not os.path.exists(path):
        return [], True
    with open(path, 'r') as f:
        return [json.loads(line) for line in f if line.strip()], False


class Source:
    """Class that syncs data & context to disk."""
    def __init__(self, context):
        self.context = context
        self.saved, self.context_is_dirty = load_jsonl(self.data_path)
        self.buffer = []
        atexit.register(self.write)
        data_sources[self.context_hash] = self
    
    @staticmethod
    def from_context(context):
        context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()
        return Source.from_hash(context_hash, context=context)
    
    @staticmethod
    def from_hash(context_hash, context=None):
        if context_hash in data_sources:
            return data_sources[context_hash]
        context = context or cached_load_json(os.path.join(storage_path(), f'{context_hash}.context.json'))
        return Source(context)
    
    @property
    def data_path(self):
        return os.path.join(storage_path(), f'{self.context_hash}.data.jsonl')
    
    def append(self, data):
        self.buffer.append(data)

    def write(self):
        if not self.buffer:
            return
        if self.context_is_dirty:
            with open(os.path.join(storage_path(), f'{self.context_hash}.context.json'), 'w') as f:
                json.dump(self.context, f, indent=4)
        with open(self.data_path, 'a') as f:
            for row in self.buffer:
                serialized = json.dumps(row)
                f.write(serialized + '\n')
        self.saved += self.buffer
        self.buffer = []
    
    @property
    def context_hash(self):
        return hashlib.sha256(json.dumps(self.context, sort_keys=True).encode()).hexdigest()
    
    @property
    def data(self):
        return self.saved + self.buffer
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, key):
        return self.data[key]

data_sources = KeyAwareDefaultDict(Source.from_hash)


class DB:
    """Logically an append only database that tracks data merged with context, and provides a few
    of all data that shares the same context."""
    _views = []

    def __init__(self, data_sources=None, context=default_context, conditions={}):
        self.dynamic_context = {
            k: v for k, v in context.items() if callable(v)
        }
        self.dynamic_context['step'] = self._default_step
        self.dynamic_context['timestamp'] = self._default_timestamp
        context = {
            k: v for k, v in context.items() if not callable(v)
        }
        context[".run_started_at"] = context.get(".run_started_at", datetime.now().isoformat())
        self.logged_data = Source.from_context(context)
        
        # data_sources: (context_hash, row_level_conditions)
        self._data_sources = data_sources
        self.conditions = conditions

        # For all other views, append (self, row_level_conditions) to their data_sources if needed
        for view in self._views:
            accept_context, row_level_conditions = view.apply_conditions_to_context(self.context_hash)
            if accept_context:
                view._data_sources.append((self.context_hash, row_level_conditions))
        DB._views.append(self)

        if len(DB._views) == 1:
            self._setup_git()
            atexit.register(self._auto_sync)
    
    @property
    def data_sources(self):
        """Lazy load data sources: data_sources is a list of (context_hash, row_level_conditions) that is used by .data"""
        if self._data_sources is not None:
            return self._data_sources
        self._data_sources = []
        for context_file in glob(os.path.join(storage_path(), '*.context.json')):
            context_hash = os.path.basename(context_file).replace('.context.json', '')
            accept_context, row_level_conditions = self.apply_conditions_to_context(context_hash)
            if accept_context:
                self._data_sources.append((context_hash, row_level_conditions))
        return self._data_sources
    
    def apply_conditions_to_context(self, context_hash, conditions={}):
        """Loads the context for a given context_hash, then checks which conditions apply on context level
        and which apply on row level. Returns a tuple of (accept_context, row_level_conditions)."""
        conditions = dict(self.conditions, **conditions)
        context = data_sources[context_hash].context
        accept_context = all([v(context[k]) for k, v in conditions.items() if k in context])
        if not accept_context:
            return False, {}
        row_level_conditions = {k: v for k, v in self.conditions.items() if k not in context}
        return True, row_level_conditions
    
    @property
    def context_hash(self):
        return self.logged_data.context_hash
    
    # @lru_cache
    def resolve(self, context_hash, row_level_conditions):
        rows = []
        src = data_sources[context_hash]
        for row in src.data:
            if all([row_level_conditions[k](v) for k, v in row_level_conditions.items()]):
                rows.append(dict(src.context, **row))
        return rows

    @property
    def data(self):
        rows = []
        for context_hash, row_level_conditions in self.data_sources:
            rows += self.resolve(context_hash, row_level_conditions)
        rows += self.logged_data.data
        return rows


    def init(self, **data: Dict[str, Any]) -> None:
        """Initialize a run with given context data."""
        db = self.get(**data)
        # Overwrite all self attributes with the new db attributes
        for key, value in db.__dict__.items():
            setattr(self, key, value)
        return self

    def log(self, data: Dict[str, Any]={}, **more_data) -> None:
        """Log data to the store."""
        data = {**data, **more_data}
        resolved = {k: v() for k, v in self.dynamic_context.items()}
        resolved.update(data)

        def process_file(value):
            if isinstance(value, File):
                return self._handle_file(value)
            elif isinstance(value, LogFile):
                return self._handle_logfile(value)
            elif isinstance(value, pd.DataFrame):
                return self._handle_dataframe(value)
            elif isinstance(value, dict):
                return {k: process_file(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_file(v) for v in value]
            else:
                return value

        processed_data = {k: process_file(v) for k, v in resolved.items()}

        # Apply the CustomJSONEncoder to the processed data but don't convert to string yet
        processed = json.dumps(processed_data, cls=CustomJSONEncoder)
        processed_data = json.loads(processed)

        self.logged_data.append(processed_data)
        return processed_data

    def _handle_logfile(self, logfile: LogFile) -> Dict[str, Any]:
        """Handle LogFile without storing immediately."""
        logfile.run_id = self.logged_data.context['run_id']
        return {
            'src': logfile.src,
            'path': logfile.path,
            'run_id': logfile.run_id,
            'filename': logfile.filename
        }

    def _handle_file(self, file: File) -> Dict[str, Any]:
        """Handle file storage and return a dictionary for logging."""
        artifacts_dir = os.path.join(storage_path(), 'artifacts')
        os.makedirs(artifacts_dir, exist_ok=True)

        dest_dir = os.path.join(artifacts_dir, file.hash)
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, os.path.basename(file.src))
        if not os.path.exists(dest_path):
            shutil.copy(file.src, dest_path)
        file.path = os.path.relpath(dest_path, storage_path())
        file.base_path = storage_path()

        return {
            'src': file.src,
            'path': file.path,
            'hash': file.hash,
            'filename': os.path.basename(file.src)
        }

    def _handle_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Handle DataFrame storage as CSV and return a dictionary for logging."""
        artifacts_dir = os.path.join(storage_path(), 'artifacts')
        os.makedirs(artifacts_dir, exist_ok=True)

        file_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
        dest_dir = os.path.join(artifacts_dir, file_hash)
        os.makedirs(dest_dir, exist_ok=True)

        filename = f"table.csv"
        dest_path = os.path.join(dest_dir, filename)
        df.to_csv(dest_path, index=False)

        return {
            'path': os.path.relpath(dest_path, storage_path()),
            'hash': file_hash,
            'filename': filename
        }

    def filter(self, conditions, new_context={}) -> 'DB':
        """Filter rows based on a dict of functions."""
        # Iterate over context files
        # Apply all conditions for keys in the context files
        # If they all pass, load the data and apply remaining conditions to rows

        filtered_data_sources = []
        for context_hash, row_level_conditions in self.data_sources:
            accept_context, new_row_level_conditions = self.apply_conditions_to_context(context_hash, conditions)
            if accept_context:
                filtered_data_sources.append((context_hash, new_row_level_conditions))
        combined_conditions = dict(self.conditions, **conditions)
        new_context = {**self.logged_data.context, **new_context}
        return DB(filtered_data_sources, new_context, combined_conditions)

    
    def get(self, **context: Dict[str, Any]) -> 'DB':
        """Get a subset of the data based on conditions."""
        condition = {k: lambda v: v == context[k] for k in context}
        return self.filter(condition, context)

    def latest(self, columns: Union[str, List[str]], index: Optional[str] = None, deep_merge: bool = True, keep_rows_without_values=False) -> Union[Dict[str, Any], pd.DataFrame]:
        """Get the latest values for the specified columns."""
        if columns == '*':
            columns = pd.DataFrame(self.data).columns
            
        single_column = None
        if isinstance(columns, str):
            single_column = columns
            columns = [columns]

        if index:
            df = pd.DataFrame(self.data)
            if (isinstance(index, str) and index not in df.columns) or (isinstance(index, list) and not all(i in df.columns for i in index)):
                # We return an empty dataframe if the index column is not present
                print(f"Index column '{index}' not found in the data.")
                print(f"Available columns: {df.columns}")
                return pd.DataFrame()

            df = get_latest_nonnull(df, index, columns)
            if not keep_rows_without_values:
                df = df.dropna(subset=columns)
            return df

        latest_data = {}
        for row in self.data:
            for column in columns:
                if column not in row:
                    continue
                if deep_merge:
                    latest_data[column] = _deep_merge(latest_data.get(column, {}), row.get(column, {}))
                else:
                    latest_data[column] = row.get(column, latest_data.get(column))

        latest_data = self._replace_files(latest_data)

        
        if single_column:
            return latest_data.get(single_column)
        else:
            return latest_data

    def _load_data(self) -> List[Dict[str, Any]]:
        data = []
        for datapath in sorted(glob(os.path.join(storage_path(), '*.jsonl'))):
            with open(datapath, 'r') as f:
                data += [json.loads(line) for line in f if line.strip()]
        return data

    def _replace_files(self, data: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
        """Replace file dictionaries with File objects."""
        if isinstance(data, dict):
            if 'path' in data and 'hash' in data and 'filename' in data:
                return File(**data, base_path=storage_path())
            else:
                return {k: self._replace_files(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_files(item) for item in data]
        else:
            return data

    def finish(self) -> None:
        """Finish the current run."""
        for item in self._logged_data:
            for key, value in item.items():
                if isinstance(value, dict) and 'src' in value and 'path' in value and 'filename' in value and value['path'].startswith('artifacts/logfile'):
                    self.log(**{key: File(value['src'])})
        self.logged_data.context.clear()
        self.sync()

    @contextmanager
    def context(self, **data: Dict[str, Any]):
        """Context manager to temporarily set context data."""
        child = self.get(**data)
        original = self.__dict__.copy()
        self.__dict__.update(child.__dict__)
        yield
        self.__dict__.update(original)

    def _default_step(self) -> int:
        """Get the current step value."""
        return self.latest('step')

    def _default_timestamp(self) -> str:
        """Get the current timestamp."""
        return datetime.now().isoformat()
    
    def _setup_git(self):
        """Initialize the git repository if it doesn't exist."""
        if not os.path.exists(os.path.join(storage_path(), '.git')):
            logger.warning(f"No git repository found at {storage_path()}. Initializing a new repository.")
            subprocess.run(['git', 'init'], cwd=storage_path())
            subprocess.run(['git', 'lfs', 'install'], cwd=storage_path())
            subprocess.run(['git', 'lfs', 'track', 'artifacts/*'], cwd=storage_path())
            subprocess.run(['git', 'add', '.gitattributes'], cwd=storage_path())
            subprocess.run(['git', 'commit', '-m', 'Initialize git repository with git-lfs'], cwd=storage_path())
        
    def sync(self):
        """Commit and push changes to the git repository."""
        with git_semaphore:
            try:
                subprocess.run(['git', 'add', '.'], cwd=storage_path())
                subprocess.run(['git', 'commit', '-m', 'Sync data'], cwd=storage_path())
                subprocess.run(['git', 'pull', '--rebase'], cwd=storage_path())
                result = subprocess.run(['git', 'push'], cwd=storage_path(), capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Git syncing skipped")
            except subprocess.CalledProcessError as e:
                logger.error(f"Git syncing skipped")

    def _auto_sync(self):
        if self == kva:
            try:
                self.sync()
            except Exception as e:
                logger.error(f"Auto sync failed: {e}")

    # For wandb compatibility
    @property
    def id(self):
        return self.latest('run_id')
    
    @property
    def config(self):
        return self.latest('config')
    
    @property
    def summary(self):
        return self.latest('*')

# Create a default DB instance for convenience
kva = DB()


def init(**data: Dict[str, Any]) -> DB:
    return kva.init(**data)

def log(data: Dict[str, Any]={}, **more_data):
    kva.log(data, **more_data)

def get(**conditions: Dict[str, Any]) -> 'DB':
    return kva.get(**conditions)

def latest(columns: Union[str, List[str]], index: Optional[str] = None, deep_merge: bool = True) -> Union[Dict[str, Any], pd.DataFrame]:
    return kva.latest(columns, index=index, deep_merge=deep_merge)

def finish() -> None:
    kva.finish()

def context(**data: Dict[str, Any]) -> None:
    kva.context(**data)

def filter(accept_row) -> 'DB':
    return kva.filter(accept_row)