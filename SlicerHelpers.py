import ast
from debuggingbook.Slicer import *
import numpy as np
from ast import *
import os

class ImportFetcher(NodeVisitor):

    def __init__(self):
        self.lineno_list = []

    def visit_Import(self, node: Import):
        if node.lineno == node.end_lineno:
            self.lineno_list.append(node.lineno)
        else:
            for linenum in range(node.lineno, node.end_lineno):
                self.lineno_list.append(linenum)

    def visit_ImportFrom(self, node: ImportFrom):
        if node.lineno == node.end_lineno:
            self.lineno_list.append(node.lineno)
        else:
            for linenum in range(node.lineno, node.end_lineno):
                self.lineno_list.append(linenum)

    def get_import_lines(self):
        return self.lineno_list


def find_import_lines(execution_log):
    code_ast = ast.parse(execution_log)
    imports = ImportFetcher()
    imports.visit(code_ast)
    return np.array(imports.get_import_lines())


def get_linenos(backwards_slice, function_start_line):
    linenos_list = []
    for piece in backwards_slice:
        linenos_list.append(piece[1][1])
    linenos_list = np.array(linenos_list)
    return linenos_list - function_start_line


def print_execution_log(execution_log):
    if type(execution_log) != str:
        return "Error: wrong data type for execution log. Should be string."
    elif not os.path.isfile(execution_log):
        return "Execution log missing."
    else:
        log_file = open(execution_log, "r")
        log_file.seek(0)
        linenum = 1
        str_to_return = ""
        for line in log_file.readlines():
            str_to_return = str_to_return + str(linenum) + INDENT + line
            linenum = linenum + 1
        log_file.close()
        print(str_to_return)


class VariableFetcher(ast.NodeVisitor):
    def __init__(self):
        self.list_of_vars = []

    def visit_Name(self, node: Name) -> Any:
        self.list_of_vars.append(node.id)

    def get_list_of_vars(self):
        return self.list_of_vars

class SliceHelper():

    _slicer = None

    def __init__(self, execution_logfile):
        True




INDENT = '    ' # indent four spaces      
        
def generate_backwards_slice(execution_log, lineno, var_to_slice='', scriptname="backwards_slice_generator.py",
                             slicename="backwards_slice.py"):
    if type(scriptname) != str or type(execution_log) != str or type(lineno) != int or type(slicename) != str:
        return "Error: wrong data type"
    else:
        if not os.path.isfile(execution_log):
            return "Execution log missing"
        if not scriptname.endswith(".py"):
            scriptname = f"{scriptname}.py"
        if not slicename.endswith(".py"):
            slicename = f"{slicename}.py"
        if os.path.isfile(scriptname):
            os.remove(scriptname)
        
        slicing_file = open(scriptname, "a+")
        
        # write import statements
        slicing_file.write("from SlicerHelpers import *\n")
        slicing_file.write("from debuggingbook.Slicer import *\n")
        slicing_file.write("import numpy as np\nimport os\nimport sys\n\n\n")

        slicing_file.write(f"if os.path.isfile(\"{slicename}\"):\n{INDENT}os.remove(\"{slicename}\")\n")
        
        # write execution log
        slicing_file.write("def test_log_for_slicing():\n")
        log_file = open(execution_log, "r")
        import_lines = find_import_lines(log_file.read())
        log_file.seek(0)
        currentline = 1
        line_string = ""
        for line in log_file.readlines():
            # may want to check which lines begin with comments and save those lines?
            slicing_file.write(INDENT + line)
            if currentline == lineno:
                line_string = line.rstrip("\n") #strip off the trailing newline character when storing the line
            currentline = currentline + 1
        log_file.close()
        slicing_file.write("\n\n")
        
        # write code to initialize Slicer, instrument execution log, and do the slice
        slicing_file.write("with Slicer(test_log_for_slicing) as slicer:\n")
        slicing_file.write(f"{INDENT}test_log_for_slicing()\n\n")
        slicing_file.write("_, start_test_log = inspect.getsourcelines(test_log_for_slicing)\n")
        if var_to_slice == '':
            slicing_file.write("var_present = True\n")
            slicing_file.write(f"slice_vars = slicer.dependencies().backward_slice((test_log_for_slicing, start_test_log + {str(lineno)})).all_vars()\n")
            slicing_file.write("if len(slice_vars) == 0:\n")
            slicing_file.write(f"{INDENT}code_ast = ast.parse(\"{line_string.strip()}\")\n") # make sure to strip away indented whitespace
            slicing_file.write(f"{INDENT}var_fetcher = VariableFetcher()\n")
            slicing_file.write(f"{INDENT}var_fetcher.visit(code_ast)\n")
            slicing_file.write(f"{INDENT}vars_list = var_fetcher.get_list_of_vars()\n")
            slicing_file.write(f"{INDENT}for var_item in vars_list:\n")
            slicing_file.write(f"{INDENT}{INDENT}var_item_slice_vars = {{}}\n")
            slicing_file.write(f"{INDENT}{INDENT}lines_done_num = 1\n")
            slicing_file.write(f"{INDENT}{INDENT}while len(var_item_slice_vars) == 0 and lines_done_num < {str(lineno)}:\n")
            slicing_file.write(f"{INDENT}{INDENT}{INDENT}var_item_slice_vars = slicer.dependencies().backward_slice((var_item, (test_log_for_slicing, start_test_log +{str(lineno)} - lines_done_num))).all_vars()\n")
            slicing_file.write(f"{INDENT}{INDENT}{INDENT}lines_done_num = lines_done_num + 1\n")
            slicing_file.write(f"{INDENT}{INDENT}slice_vars.update(var_item_slice_vars)\n")
        else:
            slicing_file.write("var_present = True\n")
            slicing_file.write(f"slice_vars = slicer.dependencies().backward_slice((\"{var_to_slice}\",(test_log_for_slicing, start_test_log + {str(lineno)}))).all_vars()\n")
            slicing_file.write("if len(slice_vars) == 0:\n")
            slicing_file.write(f"{INDENT}code_ast = ast.parse(\"{line_string.strip()}\")\n") # make sure to strip away indented whitespace
            slicing_file.write(f"{INDENT}var_fetcher = VariableFetcher()\n")
            slicing_file.write(f"{INDENT}var_fetcher.visit(code_ast)\n")
            slicing_file.write(f"{INDENT}vars_list = var_fetcher.get_list_of_vars()\n")
            slicing_file.write(f"{INDENT}if \"{var_to_slice}\" in vars_list:\n")
            slicing_file.write(f"{INDENT}{INDENT}lines_done_num = 1\n")
            slicing_file.write(f"{INDENT}{INDENT}while len(slice_vars) == 0 and lines_done_num < {str(lineno)}:\n")
            slicing_file.write(f"{INDENT}{INDENT}{INDENT}slice_vars = slicer.dependencies().backward_slice((\"{var_to_slice}\",(test_log_for_slicing, start_test_log + {str(lineno)} - lines_done_num))).all_vars()\n")
            slicing_file.write(f"{INDENT}{INDENT}{INDENT}lines_done_num = lines_done_num + 1\n")
            slicing_file.write(f"{INDENT}else:\n{INDENT}{INDENT}var_present = False\n")

        slicing_file.write("slice_linenos = get_linenos(slice_vars, start_test_log)\n")
        slicing_file.write(f"if np.size(slice_linenos) == 0:\n{INDENT}sys.exit(\"No dependencies captured. This may be due to the variable called not existing on the line number {str(lineno)}.\")\n")

        # combine slice_linenos with import linenos (import_lines)        
        slicing_file.write(f"slice_linenos = np.append(slice_linenos, np.array({np.array2string(import_lines, separator=',')}))\n")
        # add in original line checked in case it was a function
        slicing_file.write(f"slice_linenos = np.append(slice_linenos, np.array([{str(lineno)}]))\n")

        # sort linenos and remove duplicates
        slicing_file.write("slice_linenos = np.unique(slice_linenos)\n")
        slicing_file.write("slice_linenos = np.sort(slice_linenos)\n")

        # once done with combinations, write code to file to take execution log and lines to keep and generate backwards slice file.
        # open the slicename file.
        slicing_file.write(f"slice_file = open(\"{slicename}\", \"a+\")\n")
        slicing_file.write(f"log_file = open(\"{execution_log}\", \"r\")\n")
        slicing_file.write("current_line = 1\n")

        # write the linenos kept as a comment
        slicing_file.write("slice_file.write(\"# Lines Kept: \" + np.array2string(slice_linenos, separator=\",\") + \"\\n\")\n")

        slicing_file.write(f"for line in log_file.readlines():\n{INDENT}if current_line in slice_linenos:\n{INDENT}{INDENT}slice_file.write(line)\n{INDENT}current_line = current_line + 1\n")
        slicing_file.write("slice_file.close()\n")
        slicing_file.write("log_file.close()\n")
        slicing_file.close()
        # run the generated script
        os.system(f'python {scriptname}')
        # print the backward slice document
        if os.path.isfile(slicename):
            slice_file = open(slicename, "r")
            print(slice_file.read())
            slice_file.close()
            return "Slice successfully generated."
        else:
            return "Slice not generated; operation unsuccessful."

