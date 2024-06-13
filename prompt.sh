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

Can you implement the functionality where a panel has a slider - i.e. this one?
   
    - name: images-over-training
      columns: ['image'] # We assume that an image was logged as kva.log(output=File('image.png'))
      type: data 
      slider: 'step' # Slider selects the step, at each step we display with the standard data displayer"