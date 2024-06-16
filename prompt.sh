echo "I am working on the following project, and would like you to write some tests for it (using pytest)

$(cat README.md)

The backend pretty much works:

# kva/__init__.py
$(cat kva/__init__.py)

# kva/server.py
$(cat kva/server.py)

# Examples
$(concatsrc examples)

Can you turn the examples into tests and add some more tests for anything you think is missing?"
