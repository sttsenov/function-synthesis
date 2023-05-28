# Python Data Types
# (Provided by W3Schools: https://www.w3schools.com/python/python_datatypes.asp)
import inspect
import dis
import re

# Text Type: 	str
# Numeric Types: 	int, float, complex
# Sequence Types: 	list, tuple, range
# Mapping Type: 	dict
# Set Types: 	set, frozenset
# Boolean Type: 	bool
# Binary Types: 	bytes, bytearray, memoryview
# None Type: 	NoneType


def match_parameter(param_name, line):
    return re.search(rf"\b(?=\w){param_name}\b(?!\w)", line)


class OperatorClass:

    _OFFSET = 3

    # Text type
    _str_operations = dir(str)

    # Boolean type
    _bool_operations = dir(bool)

    # Mapping type
    _dict_operations = dir(dict)

    # Numeric types
    _int_operations = dir(int)
    _float_operations = dir(float)
    _complex_operations = dir(complex)

    # Sequence types
    _list_operations = dir(list)
    _tuple_operations = dir(tuple)
    _range_operations = dir(range)

    # Set types
    _set_operations = dir(set)
    _frozenset_operations = dir(frozenset)

    def record_references(self, func_object, func_body: list):
        references = []

        # Get the function's code object
        code = func_object.__code__
        # Get the names of the parameters
        param_names = code.co_varnames[:code.co_argcount]
        # Get the names of local variables within the function
        local_variables = code.co_varnames[code.co_argcount:]
        # Get the names of all built-in/library methods that get called in the function
        method_calls = code.co_names

        # Record references to parameters
        for param_name in param_names:
            # Create a dictionary representing the parameter and its references
            parameter_info = {
                'param': param_name,
                'refs': []
            }
            # Add the parameter info to the list
            references.append(parameter_info)

        instructions = list(dis.get_instructions(code))
        possible_method_calls = []
        noted_method_calls = []

        for instr in instructions:
            print(instr)
            # Get only operations that store value
            if instr.opname.startswith('STORE_') and instr.argval is not None:
                # Get the actual line of code (done after the if because negative indexes are a thing)
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                for ref in references:
                    if match_parameter(ref['param'], code_line):
                        ref['refs'] .append(instr.argval)  # dumb ass naming

            elif instr.opname.__eq__('LOAD_GLOBAL') and instr.argval is not None:
                if instr.argval in method_calls:
                    code_line = func_body[instr.positions.lineno - self._OFFSET]
                    possible_method_calls.append(code_line)

        # Check if any of the parameters have been used in a method call
        for method_line in possible_method_calls:

            # TO-DO: Check here that it's one of the methods that we have as attributes

            for ref in references:
                if match_parameter(ref['param'], method_line):
                    # TO-DO: Somehow change the line so we only get the method name
                    noted_method_calls.append(method_line)

        print(f'METHOD CALLS: {noted_method_calls}')
        return references

