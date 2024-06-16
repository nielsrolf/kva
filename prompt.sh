echo "I am working on the following project:

$(cat README.md)

The backend pretty much works:

# kva/__init__.py
$(cat kva/__init__.py)

# kva/server.py
$(cat kva/server.py)

# UI
$(concatsrc frontend/src/ --ext .js)


I am currently having issues omn the RunDetail view when a table is being displayed: I get "react-dom.production.min.js:188 TypeError: t.slice is not a function" in this line:
> const currentData = data.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

Can you help me fix that?"
