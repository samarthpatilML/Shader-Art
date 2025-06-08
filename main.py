import random
import matplotlib.pyplot as plt

# Transformation functions with their probabilities
functions = [
    {"matrix": [[0.00, 0.00], [0.00, 0.16]], "shift": [0, 0], "prob": 0.01},
    {"matrix": [[0.85, 0.04], [-0.04, 0.85]], "shift": [0, 1.6], "prob": 0.85},
    {"matrix": [[0.20, -0.26], [0.23, 0.22]], "shift": [0, 1.6], "prob": 0.07},
    {"matrix": [[-0.15, 0.28], [0.26, 0.24]], "shift": [0, 0.44], "prob": 0.07},
]

def apply_function(x, y, func):
    a, b = func["matrix"][0]
    c, d = func["matrix"][1]
    e, f = func["shift"]
    x_new = a * x + b * y + e
    y_new = c * x + d * y + f
    return x_new, y_new

def generate_ifs(n_points=100000):
    x, y = 0, 0
    xs, ys = [], []

    for _ in range(n_points):
        r = random.random()
        total = 0
        for func in functions:
            total += func["prob"]
            if r <= total:
                x, y = apply_function(x, y, func)
                xs.append(x)
                ys.append(y)
                break

    return xs, ys

# Generate and plot
xs, ys = generate_ifs()
plt.figure(figsize=(6, 10))
plt.scatter(xs, ys, s=0.1, color='green')
plt.title("Barnsley Fern - IFS")
plt.axis("off")
plt.show()
import random
import matplotlib.pyplot as plt

# Transformation functions with their probabilities
functions = [
    {"matrix": [[0.00, 0.00], [0.00, 0.16]], "shift": [0, 0], "prob": 0.01},
    {"matrix": [[0.85, 0.04], [-0.04, 0.85]], "shift": [0, 1.6], "prob": 0.85},
    {"matrix": [[0.20, -0.26], [0.23, 0.22]], "shift": [0, 1.6], "prob": 0.07},
    {"matrix": [[-0.15, 0.28], [0.26, 0.24]], "shift": [0, 0.44], "prob": 0.07},
]

def apply_function(x, y, func):
    a, b = func["matrix"][0]
    c, d = func["matrix"][1]
    e, f = func["shift"]
    x_new = a * x + b * y + e
    y_new = c * x + d * y + f
    return x_new, y_new

def generate_ifs(n_points=100000):
    x, y = 0, 0
    xs, ys = [], []

    for _ in range(n_points):
        r = random.random()
        total = 0
        for func in functions:
            total += func["prob"]
            if r <= total:
                x, y = apply_function(x, y, func)
                xs.append(x)
                ys.append(y)
                break

    return xs, ys

# Generate and plot
xs, ys = generate_ifs()
plt.figure(figsize=(6, 10))
plt.scatter(xs, ys, s=0.1, color='green')
plt.title("Barnsley Fern - IFS")
plt.axis("off")
plt.show()
