echo "I am working on the following project:

$(cat README.md)

The backend pretty much works:

# kva/__init__.py
$(cat kva/__init__.py)

# kva/test_core.py
$(cat kva/test_core.py)

This pretty much works, but sometimes I get errors when I try to log stuff that isn't natively json serializable.
Can you implement a custom JSONEncoder that can handle the following types:
- datetime dates and times
- torch tensors
- numpy arrays
- hydra configs
- any other custom types you can think of that should get custom treatment
- every other object should be serialized be pickled annd logged as an artifact

Please start with the test cases."
