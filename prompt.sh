echo "I am working on the following experiment:

$(cat README.md)

The backend pretty much works:

# kva/__init__.py
$(cat kva/__init__.py)

# kva/server.py
$(cat kva/server.py)

# UI
$(concatsrc frontend/src/ --ext .js)


Now I would like to make it simpler to log tables. Consider this example:
$(cat examples/tables.py)

In order to make this work, we should do the following:
- create a kva.Table class that is a subclass of a pd.DataFrame and has an interface compatible with the one in the example (this is the interface wandb tables have)
- make it such that when DataFrames are logged, we save them as a CSV file and treat them like files
- in the UI: in FilePanel, when a file is a CSV, render them as a table

Can you implement this?"
