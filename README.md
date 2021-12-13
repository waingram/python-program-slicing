# Minimal Program Extraction from Computational Notebooks

Computational notebooks are popular tools for data scientists, especially for  exploratory data analysis. 
This iterative process can lead to messy notebooks. 
As the amount of code grows, many developers struggle to keep track of their experimentation, resulting in confusion about how results were obtained. 
We propose using program slicing to help developers identify the code statements that may be relevant to the variables at a particular point in the program. 
Once the program slice is isolated, developers can use it to debug a fault in their code, or they may want to extract the slice and copy it to a new, clean notebook. 
  
Check out the demo [here](https://github.com/waingram/python-program-slicing/blob/b25bf71fc22853635a0742a2cf18b8b75cbd10c4/program_slice_demo.ipynb). 

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

### Create the execution log 

To create an execution log from your Jupyter Notebook execution, use the following custom IPython Magics. 

```python
from IPython.core.magic import register_cell_magic

@register_cell_magic
def write_and_run(line, cell):
    """Write the contents of a cell to a file, but only if the execution succeeds without error. 
    
    -a is an optional parameter, which opens the file in append mode.   
    
    e.g., %%write_and_run -a execution_log.py
    
    """
    argz = line.split()
    file = argz[-1]
    mode = 'w'
    if len(argz) == 2 and argz[0] == '-a':
        mode = 'a'
        
    result = get_ipython().run_cell(cell)
    
    if result.error_in_exec is None:
        with open(file, mode) as f:
            f.write(cell)
```

Then, at the beginning of every cell, use the magics command. 

```python
%%write_and_run -a execution_log.py
```

### Compute the program slice 

```python
from SlicerHelpers import *

# print execution log from your Jupyter notebook
print_execution_log('execution_log.py')

# generate backwards slice 
generate_backwards_slice('execution_log.py', 13)

```


## License
[BSD-3-Clause License](https://github.com/waingram/python-program-slicing/blob/LICENSE)