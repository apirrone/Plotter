# Plotter

A  very simple live plotter

https://user-images.githubusercontent.com/6552564/187200679-3aa8d1f9-b530-4bb6-a394-475bfcd902e0.mp4
## So simple

```python
from Plotter import Plotter

plotter = Plotter()
plotter.start() # The plot runs in a separate thread

while True:
    ...
    ...
    plotter.push(t, value1[i], "value1", [0, 1, 0])
    plotter.push(t, value2[i], "value2", [0, 0, 1])
```

## TODO
- handle negative numbers
- background for legend
- use RGB instead of BGR when function is meant to be used by user
