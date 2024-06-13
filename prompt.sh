echo "I am working on the following experiment:

$(cat README.md)

The backend pretty much works:

# kva.py
$(cat kva.py)

# server.py
$(cat server.py)


Now, I am working on a simple UI:
$(cat ui.md)

A basic version is partly implemented:
$(concatsrc frontend/src/ --ext .js)

Now I would like to make some small usability changes:
- the first page should have a search/filter field where I can write regex strings like 'model*-version*'
- On the detail page, there should be a button to go back to the list page"
