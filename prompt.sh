echo "I am working on the following project:

$(cat README.md)

# --- kva/__init__.py
\`\`\`
$(cat kva/__init__.py)
\`\`\`


# --- kva/utils.py
\`\`\`python
$(cat kva/utils.py)
\`\`\`

# --- Tests
\`\`\`python
$(cat kva/test_core.py)
\`\`\`

# --- UI

\`\`\`python
$(cat kva/server.py)
\`\`\`

$(concatsrc frontend/src/ --ext js)


I would like to create a new class 'LogFile' that behaves in the following way:
\`\`\`
kva.init(run_id='my-run')
kva.log(stdout=LogFile("stdout.txt"))
\`\`\`
- stdout.txt is not saved to the artifacts folder until .finish is called - we only save the original src
- when logged, the path should be set to logfiles/<runid>/<filename>
- the frontend will request the file via its path (which is not set initially), therefore we set the path to logfiles/<runid>/<filename> and handle this in the server
- in kva.finish, we then call self.log(stdout=File(logfile.src)) to save the file to the artifacts folder
- In the frontend, I should see a 'stdout' that updates on refresh while the run is in progress by fetching /logfiles/<runid>/<filename>, and when it is done it should look the same but now fetch it from /artifacts/<hash>/<filename>
Can you implement this?"
