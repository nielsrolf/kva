# A simple key-value-artifact store

KVA is a simple key-value-artifact store designed to log and retrieve data. It is like wandb, but not so shitty.
At its heart, it is a append-only JSON store with some helpers to easily retrieve data and handle files.

## Examples
```python
from kva import kva

kva.init(run_id="some-run")
kva.log(config={'foo': 'bar'})
# Oups there was something missing in the config
kva.log(config={'hello': 'world'})
kva.log(step=1, loss=42)
kva.log(step=2)
kva.log(loss=4.2)
print(kva.get(run_id="some-run").latest('config'))
# {'foo': 'bar', 'hello': 'world'}
print(kva.get(run_id="some-run").latest('config', deep_merge=False))
# {'hello': 'world'}
print(kva.get(run_id="some-run").latest('loss'))
# 4.2
print(kva.get(run_id="some-run").latest(['loss', 'step']))
# {'loss': 4.2, 'step': 1}
print(kva.get(run_id="some-run").latest('loss', index='step')) # Identical to: .latest(['loss'], index=['step'])
#    step  loss
# 0   1.0  42.0
# 1   2.0   4.2
```

# Setup

## Install
```
pip install kva
```

## Configure backend

For local storage, set:
```
export KVA_STORAGE='~/.kva' # Default
```

For online storage, set:
```
export KVA_STORAGE='https://supabase.endoint.org'
```

## Using with git or git-lfs
When configured to stora data locally, kva stores data in a git friendly way:
```
data.jsonl
artifacts/{filehash}/filename.fileextension
```

# Docs
## Core methods

### `kva.log(**data)`
Appends `dict(**data, **init_data)` to the append-only database.
Every value that is a `kva.File` (or a subclass thereof) is additionally saved.


### `kva.filter(accept_row)`
Filters the rows of the database for exact matches and returns a `kva.DB` object.

### `db.latest()`
Returns a view of the data in the `db`:
```
kva.DB().latest(
    columns, # Which values to get
    index=None, # If set, returns a dataframe of latest values in the db for each value of the index
    deep_merge=True # Wether or not to merge data of different rows or only select the latest row
)
``` 

### `with kva.context(**data)`
Adds `data` to subsequent calls of `kva.log`.

## Convenience

### `kva.get(**keys)`
A wrapper for `kva.filter(f)` where the `f` checks if all values of a row are identical to values in `keys`.

### `kva.init(**data)`
Basically another way of calling `with kva.context(**data)`:
- starts a run that remains active until `kva.finish()` is called.
- subsequent calls to `kva.log(**other_data)` also log `**data`
- therefore you can use it like this:

### `kva.log_artifact(path)`
- the same as: `kva.log(kva.File(path))`
