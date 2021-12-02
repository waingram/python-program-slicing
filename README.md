# Minimal Program Extraction from Computational Notebooks

Computational notebooks are popular tools for data scientists, especially for  exploratory data analysis. 
This iterative process can lead to messy notebooks. 
As the amount of code grows, many developers struggle to keep track of their experimentation, resulting in confusion about how results were obtained. 
We propose using program slicing to help developers identify the code statements that may be relevant to the variables at a particular point in the program. 
Once the program slice is isolated, developers can use it to debug a fault in their code, or they may want to extract the slice and copy it to a new, clean notebook. 

## Installation

1. Create the environment from the `environment.yml` file. 
2. Activate the environment. 
3. Run JupyterLab.

```Shell
conda env create -f environment.yml
conda activate python-program-slicing

jupyter lab
```

## Usage

```python
from SlicerHelpers import *

# print execution log from your Jupyter notebook
print_execution_log('execution_log.py')

# generate backwards slice 
generate_backwards_slice('execution_log.py', 13)

```


## License
[BSD-3-Clause License](https://github.com/waingram/python-program-slicing/blob/LICENSE)