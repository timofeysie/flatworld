# Flatworld

## Useful Terms

- Fuzzy logic
- Subsumption
- The genetic algorithm 
- [Perceptron](https://en.wikipedia.org/wiki/Perceptron)
- Sigmoid

## Running the Neural Flatworld

The `NeuralFlatworld.py` script requires TensorFlow, which needs Python 3.12 or earlier (TensorFlow doesn't support Python 3.14+). A virtual environment has been set up with all required dependencies.

### Prerequisites

The virtual environment (`venv`) includes:
- TensorFlow 2.20.0
- NumPy (installed as a TensorFlow dependency)
- Pygame 2.6.1
- TensorFlow Datasets, Pillow, and Matplotlib

### Running the Script

**Option 1: Activate the virtual environment first (recommended)**

```bash
cd "/Users/timo/repos/python/AI for Devs book"
source venv/bin/activate
python NeuralFlatworld.py
```

**Option 2: Run directly with the virtual environment's Python**

```bash
cd "/Users/timo/repos/python/AI for Devs book"
venv/bin/python NeuralFlatworld.py
```

### Deactivating the Virtual Environment

When you're done, you can deactivate the virtual environment with:

```bash
deactivate
```

### Troubleshooting

If you encounter a `ModuleNotFoundError: No module named 'tensorflow'`, make sure you're using the virtual environment's Python interpreter. The system Python 3.14 doesn't have TensorFlow installed and isn't compatible with TensorFlow.
