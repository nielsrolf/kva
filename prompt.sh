echo "I am working on the following project:

$(cat README.md)

Currently, all data is appended to a single jsonl file in the data directory. This works fine on a single instance, but leads to merge conflicts when git is synced:

# --- kva/__init__.py
```python
$(cat kva/__init__.py)
```

# --- kva/utils.py
```python
$(cat kva/utils.py)
```

# --- Tests
```python
$(cat kva/test_core.py)
```

I would like to  make the following changes:
- we load data lazily from all data_{timestamp}.jsonl files, making .data() a @property
    - when no data has been passed to the constructor, it reads all data_{timestamp}.jsonl files
    - otherwise it takes the data passed to the constructor (saved in ._data)
    - data logged directly via .log is saved to ._unsaved_data, and also used by .data()
- whenever we log data to a file, we use a data path that was created in the constructer

Can you implement these changes?"
