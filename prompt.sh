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

Can you add some basic styling? I.e.
- table cells should have a border
- panels should be foldable (hide an entire panel)
- Use some nicer fonts and do some general styling (not black on white, etc)"