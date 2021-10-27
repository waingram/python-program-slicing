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

def writeBackwardsSlice(lines_to_keep):
    pass


def write_execution_log(execution_log, writing_file):
    pass



def generate_backwards_slice(execution_log, lineno, scriptname="backwards_slice_generator.py", slicename="backwards_slice.py"):
    if type(scriptname) != str or type(execution_log) != str or type(lineno) != int or type(slicename) != str:
        return "Error: wrong data type"
    else:
        if not os.path.isfile(execution_log):
            return "Execution log missing"
        if not scriptname.endswith(".py"):
            scriptname = scriptname + ".py"
        if not slicename.endswith(".py"):
            slicename = slicename + ".py"
        if os.path.isfile(scriptname):
            os.remove(scriptname)
        slicing_file = open(scriptname, "a+")
        #write import statements
        slicing_file.write("from SlicerHelpers import *\n")
        slicing_file.write("from debuggingbook.Slicer import *\n")
        slicing_file.write("import numpy as np\nimport os\n\n\n")
        #write execution log
        slicing_file.write("def test_log_for_slicing():\n")
        log_file = open(execution_log, "r")
        import_lines = find_import_lines(log_file.read())
        log_file.seek(0)
        for line in log_file.readlines():
            # may want to check which lines begin with comments and save those lines?
            slicing_file.write("\t" + line)
        log_file.close()
        slicing_file.write("\n\n")
        slicing_file.write("with Slicer(test_log_for_slicing) as slicer:\n")
        slicing_file.write("\ttest_log_for_slicing()\n\n")
        slicing_file.write("_, start_test_log = inspect.getsourcelines(test_log_for_slicing)\n")
        slicing_file.write("slice_vars = slicer.dependencies().backward_slice((test_log_for_slicing, start_test_log + " + str(lineno) + ")).all_vars()\n")
        slicing_file.write("slice_linenos = get_linenos(slice_vars, start_test_log)\n")
        # combine slice_linenos with import linenos (import_lines)
        slicing_file.write("slice_linenos = np.append(slice_linenos, np.array(" + np.array2string(import_lines, separator = ",") + "))\n")
        # once done with combinations, write code to file to take execution log and lines to keep and generate backwards slice file.
        # start by checking if slicename file exists and removing it if it does. Then open the slicename file.
        slicing_file.write("if os.path.isfile(\"" + slicename + "\"):\n\tos.remove(\"" + slicename + "\")\n")
        slicing_file.write("slice_file = open(\"" + slicename + "\", \"a+\")\n")
        slicing_file.write("log_file = open(\"" + execution_log + "\", \"r\")\n")
        slicing_file.write("current_line = 1\n")
        slicing_file.write("for line in log_file.readlines():\n\tif current_line in slice_linenos:\n\t\tslice_file.write(line)\n\tcurrent_line = current_line + 1\n")
        slicing_file.write("slice_file.close()\n")
        slicing_file.write("log_file.close()\n")
        slicing_file.close()
        # run the generated script
        os.system(scriptname)
        #print the backward slice document
        if os.path.isfile(slicename):
            slice_file = open(slicename, "r")
            print(slice_file.read())
            slice_file.close()





