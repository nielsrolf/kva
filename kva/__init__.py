# kva/__init__.py
import os
import json
import hashlib
from typing import Any, Dict, List, Union, Optional
import pandas as pd
from contextlib import contextmanager
from datetime import datetime
import shutil
import uuid

class Table(pd.DataFrame):
    def add_row(self, **kwargs):
        new_row = pd.DataFrame([kwargs], columns=self.columns)
        self._update_inplace(new_row)


class File(dict):
    def __init__(self, src: Optional[str] = None, path: Optional[str] = None, hash: Optional[str] = None, filename: Optional[str] = None, base_path: Optional[str] = None):
        self.src = src
        self.path = path
        self.hash = hash or self._calculate_hash(src)
        self.filename = filename or os.path.basename(src)
        self.base_path = base_path
        
        super().__init__(src=self.src, path=self.path, hash=self.hash, filename=self.filename)
    
    def __repr__(self):
        return f'File(src={self.src!r}, path={self.path!r}, hash={self.hash!r}, filename={self.filename!r})'

    @staticmethod
    def _calculate_hash(path: str) -> str:
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def as_df(self):
        if self.base_path is None or self.path is None:
            raise ValueError("Can only get the dataframe after a table has been logged.")
        return pd.read_csv(os.path.join(self.base_path, self.path))


class Folder(dict):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self._populate()

    def _populate(self):
        for item in os.listdir(self.path):
            item_path = os.path.join(self.path, item)
            if os.path.isdir(item_path):
                self[item] = Folder(item_path)
            else:
                self[item] = File(item_path)

    def __repr__(self):
        return f'Folder(path={self.path!r}, contents={list(self.keys())!r})'



def _deep_merge(a: Any, b: Any) -> Any:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in b:
            a[key] = _deep_merge(a.get(key), b[key])
        return a
    return b


def latest_or_none(series: pd.Series, *functions) -> Any:
    series = series[~series.isnull()]
    val = series.iloc[-1] if not series.empty else None
    for func in functions:
        val = func(val)
    return val


def get_latest_nonnull(df, index, columns):
    columns = [c for c in columns if c in df.columns]
    def last_nonnull(series):
        return series.dropna().iloc[-1] if not series.dropna().empty else None
    
    grouped = df.groupby(index)
    result = grouped[columns].apply(lambda group: group.apply(last_nonnull))
    # Filter out rows where all columns are None
    result = result.dropna(how='all')
    # If no columns are left, return an empty dataframe
    if result.empty:
        return pd.DataFrame()
    return result.reset_index()


class DB:
    _views = []
    
    def __init__(self, storage: Optional[str] = None, data=None):
        self.storage = storage or os.getenv('KVA_STORAGE', '~/.kva')
        self.storage = os.path.expanduser(self.storage)
        os.makedirs(self.storage, exist_ok=True)
        self.storage = os.path.expanduser(self.storage)
        self.db_file = os.path.join(self.storage, 'data.jsonl')
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.context_data = {}
        self.context_stack = []
        self.default_context = {
            'step': self._default_step,
            'timestamp': self._default_timestamp
        }
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                pass
        self.data = self._load_data() if data is None else data
        DB._views.append(self)

    def init(self, **data: Dict[str, Any]) -> None:
        """Initialize a run with given context data."""
        self.context_data.update(self.default_context)
        self.context_data.update(data)
        if not 'run_id' in self.context_data:
            self.context_data['run_id'] = uuid.uuid4().hex[:8]
        return self.get(**data)

    def log(self, data: Dict[str, Any]={}, **more_data) -> None:
        """Log data to the store."""
        data = {**data, **more_data}
        resolved = {k: (v() if callable(v) else v) for k, v in self.context_data.items()}
        resolved.update(data)

        def process_file(value):
            if isinstance(value, File):
                return self._handle_file(value)
            elif isinstance(value, pd.DataFrame):
                return self._handle_dataframe(value)
            elif isinstance(value, dict):
                return {k: process_file(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_file(v) for v in value]
            else:
                return value

        processed_data = {k: process_file(v) for k, v in resolved.items()}

        with open(self.db_file, 'a') as f:
            f.write(json.dumps(processed_data) + '\n')
        for view in DB._views:
            if view.storage == self.storage:
                view.data.append(processed_data)

    def _handle_file(self, file: File) -> Dict[str, Any]:
        """Handle file storage and return a dictionary for logging."""
        artifacts_dir = os.path.join(self.storage, 'artifacts')
        os.makedirs(artifacts_dir, exist_ok=True)

        dest_dir = os.path.join(artifacts_dir, file.hash)
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, os.path.basename(file.src))
        if not os.path.exists(dest_path):
            shutil.copy(file.src, dest_path)
        file.path = os.path.relpath(dest_path, self.storage)
        file.base_path = self.storage

        return {
            'src': file.src,
            'path': file.path,
            'hash': file.hash,
            'filename': os.path.basename(file.src)
        }

    def _handle_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Handle DataFrame storage as CSV and return a dictionary for logging."""
        artifacts_dir = os.path.join(self.storage, 'artifacts')
        os.makedirs(artifacts_dir, exist_ok=True)

        file_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
        dest_dir = os.path.join(artifacts_dir, file_hash)
        os.makedirs(dest_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex[:8]}.csv"
        dest_path = os.path.join(dest_dir, filename)
        df.to_csv(dest_path, index=False)

        return {
            'path': os.path.relpath(dest_path, self.storage),
            'hash': file_hash,
            'filename': filename
        }

    def filter(self, accept_row) -> 'DB':
        """Filter rows based on a function."""
        db = DB(storage=self.storage, data=[row for row in self.data if accept_row(row)])
        db.context_data = self.context_data.copy()
        return db
    
    def get(self, **conditions: Dict[str, Any]) -> 'DB':
        """Get a subset of the data based on conditions."""
        def condition(row):
            return all(row.get(k) == v for k, v in conditions.items())
        return self.filter(condition)

    def latest(self, columns: Union[str, List[str]], index: Optional[str] = None, deep_merge: bool = True) -> Union[Dict[str, Any], pd.DataFrame]:
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
                return pd.DataFrame()

            df = get_latest_nonnull(df, index, columns)
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
        with open(self.db_file, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]

    def _replace_files(self, data: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
        """Replace file dictionaries with File objects."""
        if isinstance(data, dict):
            if 'path' in data and 'hash' in data and 'filename' in data:
                return File(**data, base_path=self.storage)
            else:
                return {k: self._replace_files(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_files(item) for item in data]
        else:
            return data

    def finish(self) -> None:
        """Finish the current run."""
        self.context_data.clear()

    @contextmanager
    def context(self, **data: Dict[str, Any]):
        """Temporarily add data to the context."""
        # Save current context
        old_context = self.context_data.copy()
        self.context_stack.append(old_context)

        # Update context
        self.context_data.update(data)

        try:
            yield
        finally:
            # Restore previous context
            self.context_data = self.context_stack.pop()

    def _default_step(self) -> int:
        """Get the current step value."""
        return self.latest('step')

    def _default_timestamp(self) -> str:
        """Get the current timestamp."""
        return datetime.now().isoformat()
    
    # For wandb compatibility
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
