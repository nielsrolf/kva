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

Now I am working on this slider feature:
   
    - name: images-over-training
      columns: ['image'] # We assume that an image was logged as kva.log(output=File('image.png'))
      type: data 
      slider: 'step' # Slider selects the step, at each step we display with the standard data displayer

Currently, this is broken:
- It renders what seems to be two YamlPanel views - an initial one, then a slider, then the same again
- I think this is because we don't check if !slider in the Panel
- but there is also the issue that the SliderPanel that should be rendered currently looks like a normal YamlPanel with a slider that has no effect

Can you fix this?"