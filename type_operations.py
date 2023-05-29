# Python Data Types
# (Provided by W3Schools: https://www.w3schools.com/python/python_datatypes.asp)
import dis
import re

# Text Type: 	str
# Numeric Types: 	int, float, complex
# Sequence Types: 	list, tuple, range
# Mapping Type: 	dict
# Set Types: 	set, frozenset
# Boolean Type: 	bool
# Binary Types: 	bytes, bytearray, memory view
# None Type: 	NoneType


def match_parameter(param_name, line):
    return re.search(rf"\b(?=\w){param_name}\b(?!\w)", line)


def check_method_takes_args(method_name: str, code_line: str):
    return not code_line.split(method_name)[-1].startswith('()')


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

    _OPERATIONS = {
        # Text type
        'str': dir(str),
        # Boolean type
        'bool': dir(bool),
        # Mapping type
        'dict': dir(dict),
        # Numeric types
        'int': dir(int),
        'float': dir(float),
        'complex': dir(complex),
        # Sequence types
        'list': dir(list),
        'tuple': dir(tuple),
        'range': dir(range),
        # Set types
        'set': dir(set),
        'frozenset': dir(frozenset)
    }

    def check_builtin_methods(self, method_name: str):
        possible_types = []
        method_name = method_name.lstrip().rstrip()

        # Check if the method can be found in the builtin methods
        # for the recorded data types
        for type_str, operations in self._OPERATIONS.items():
            # Decided to use a loop instead of a 'str in list' check
            # just to be able to break out early
            for op in operations:
                if method_name.__eq__(op):
                    possible_types.append(type_str)
                    break

        return possible_types

    def record_references(self, func_object, func_body: list):
        """
        This records the parameters, variables that refers them and methods
        that are used by the parameters or reference variables.

        NOTE: At some point this should be done recursively so that it can note
        all the references to parameters. For example:

        x = param0.upper() -> gets recorded
        y = x.startswith('...') -> does NOT get recorded

        :param func_object: allows to get the code instructions and arguments
        :param func_body: allows to get the actual line of code inside the body
        :return: a reference map
        """
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
                'refs': [],
                'method_calls': []
            }
            # Add the parameter info to the list
            references.append(parameter_info)

        instructions = list(dis.get_instructions(code))
        possible_method_calls = []

        for instr in instructions:
            print(instr)
            # Get only operations that store value
            if instr.opname.startswith('STORE_') and instr.argval is not None:
                # Get the actual line of code (done after the if because negative indexes are a thing)
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                for ref in references:
                    if match_parameter(ref['param'], code_line):
                        ref['refs'] .append(instr.argval)  # dumb ass naming

            elif instr.opname.__eq__('LOAD_METHOD') and instr.argval is not None:
                if instr.argval in method_calls:
                    code_line = func_body[instr.positions.lineno - self._OFFSET]
                    possible_method_calls.append({
                        'name': instr.argval,
                        'line': code_line.replace('\n', '')
                    })
        # Check if any of the parameters have been used in a method call
        for method_info in possible_method_calls:
            method_name = method_info['name']
            method_line = method_info['line']

            builtin_method_types = self.check_builtin_methods(method_name)
            # No point in continuing if we cannot map the method
            if len(builtin_method_types) == 0:
                break

            takes_args = check_method_takes_args(method_name, method_line)
            method_dict = {
                'method': method_info,
                'possible_types': builtin_method_types,
                'takes_arguments': takes_args,
                'level': 0  # Refers to a direct parameter reference
            }

            for ref in references:
                noted_method_calls = []
                if match_parameter(ref['param'], method_line):
                    noted_method_calls.append(method_dict)

                # Don't judge my naming conventions, I already judge them
                for r in ref['refs']:
                    if match_parameter(r, method_line):
                        method_dict['level'] = 1    # Refers to an indirect parameter reference
                        noted_method_calls.append(method_dict)
                        break
                ref['method_calls'].extend(noted_method_calls)

        return references
