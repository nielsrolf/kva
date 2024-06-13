from kva import kva, File


import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, max_iter):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n

def generate_mandelbrot_image(num_iter):
    width, height = 800, 800
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5

    x, y = np.linspace(x_min, x_max, width), np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    mandelbrot_set = np.frompyfunc(lambda c: mandelbrot(c, num_iter), 1, 1)(C).astype(np.float32)

    plt.imshow(mandelbrot_set, extent=(x_min, x_max, y_min, y_max), cmap='inferno')
    plt.axis('off')
    plt.colorbar()
    plt.title(f"Mandelbrot Set with {num_iter} iterations")
    plt.savefig('mandelbrot.png')
    plt.close()



kva.init(run_id="Mandelbrot")
kva.log(config={'foo': 'bar', 'hello': 'world'})


for step in range(100):
    kva.log(step=step, square=step**2)
    kva.log(loss=1/(step+1))

    if step % 10 == 0:
        generate_mandelbrot_image(step)
        kva.log(image=File('mandelbrot.png'))

df = kva.get(run_id="Mandelbrot").latest(['loss', 'square'], index='step')
print(df)