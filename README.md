# Plotter

A  very simple live plotter

## So simple

```python
from Plotter import Plotter
plotter = Plotter()

while True:
    ...
    ...
    plotter.push(i, value1[i], "value1", [0, 1, 0])
    plotter.push(i, value2[i], "value2", [0, 0, 1])
```

## TODO
- handle negative numbers
- background for legend
- use RGB instead of BGR when function is meant to be used by user
