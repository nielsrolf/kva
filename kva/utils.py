import hashlib
import json
import os
import pickle
import shutil
import uuid
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, List, Optional, Union

import pandas as pd

DEFAULT_STORAGE = "/workspace/kva_store" if os.path.exists("/workspace") else "~/.kva"
if os.environ.get("KVA_STORAGE"):
    DEFAULT_STORAGE = os.environ["KVA_STORAGE"]

logger = getLogger(__name__)


def set_default_storage(kva, path: str):
    global DEFAULT_STORAGE
    DEFAULT_STORAGE = path
    kva.storage = path
    os.makedirs(path, exist_ok=True)
    

class Table(pd.DataFrame):
    def add_row(self, *values, **data):
        data = dict(zip(self.columns, values), **data)
        new_row = pd.DataFrame([data], columns=self.columns)
        self._update_inplace(pd.concat([self, new_row], ignore_index=True))


class File(dict):
    def __init__(
        self,
        src: Optional[str] = None,
        path: Optional[str] = None,
        hash: Optional[str] = None,
        filename: Optional[str] = None,
        base_path: Optional[str] = None,
    ):
        self.src = src
        self.path = path
        self.hash = hash or self._calculate_hash(src)
        self.filename = filename or os.path.basename(src)
        self.base_path = base_path

        super().__init__(
            src=self.src, path=self.path, hash=self.hash, filename=self.filename
        )

    def __repr__(self):
        return f"File(src={self.src!r}, path={self.path!r}, hash={self.hash!r}, filename={self.filename!r})"

    @staticmethod
    def _calculate_hash(path: str) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def as_df(self):
        if self.base_path is None or self.path is None:
            raise ValueError(
                "Can only get the dataframe after a table has been logged."
            )
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
        return f"Folder(path={self.path!r}, contents={list(self.keys())!r})"


def _deep_merge(a: Any, b: Any) -> Any:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in b:
            a[key] = _deep_merge(a.get(key), b[key])
        return a
    return b


class Container:
    def __init__(self, val):
        self.val = val


def get_latest_nonnull(df, index: Union[List[str], str], columns: List[str]):
    """Gets a dataframe and returns a new dataframe where:
    - the df is grouped by the index columns
    - for each of the columns, the last non-null value of the group is taken
    The result is a dataframe with the specified index and columns, where the values are the last non-null values of the group.
    """
    columns = [col for col in columns if col in df.columns]
    if isinstance(index, str):
        index = [index]
    index = [col for col in index if col in df.columns]
    if not index or not columns:
        return pd.DataFrame()

    def last_non_null(series):
        val = series.dropna().iloc[-1] if not series.dropna().empty else None
        if isinstance(val, dict):
            return Container(val)
        else:
            return val

    grouped = df.groupby(index)
    result = grouped[columns].apply(lambda x: x.apply(last_non_null))

    # Unpack Container objects
    def unpack(val):
        if isinstance(val, Container):
            return val.val
        return val

    result = result.map(unpack)
    return result


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            obj = obj.to("cpu").detach().numpy()
        except TypeError:
            obj = obj.to(dtype=torch.float32).to("cpu").detach().numpy()
        except AttributeError:
            pass
        try:
            return obj.tolist()
        except AttributeError:
            pass
        try:
            return obj.isoformat()
        except AttributeError:
            pass
        try:
            return obj.to_container()
        except AttributeError:
            pass
        try:
            return self._handle_custom_object(obj)
        except AttributeError:
            pass
        logger.warning(
            f"Object of type {type(obj)} with value {obj} is not JSON serializable."
        )
        return obj.__dict__

    def _handle_custom_object(self, obj):
        # Pickle the object and store it as an artifact
        file_path = self._pickle_object(obj)
        file = File(
            src=file_path,
            path=os.path.relpath(file_path, DEFAULT_STORAGE),
            filename=os.path.basename(file_path),
        )
        return file

    def _pickle_object(self, obj):
        # Generate a unique filename based on the object's class name and a UUID
        filename = f"{obj.__class__.__name__}_{uuid.uuid4().hex}.pkl"
        file_path = os.path.join(DEFAULT_STORAGE, "artifacts", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            pickle.dump(obj, f)

        return file_path
