import dis
import re


# Python Data Types
# (Provided by W3Schools: https://www.w3schools.com/python/python_datatypes.asp)

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


def make_method_dict(method_info: dict, builtin_method_types):
    takes_args = check_method_takes_args(method_info['name'], method_info['line'])
    method_dict = {
        'method': method_info,
        'possible_types': builtin_method_types,
        'takes_arguments': takes_args,
        'level': 0  # Refers to a direct parameter reference
    }

    return method_dict


def match_subscribe_operation(instr_name: str) -> str:
    if instr_name.__eq__('DELETE_SUBSCR'):
        return '__delitem__'
    elif instr_name.__eq__('BINARY_SUBSCR'):
        return '__getitem__'

    return '__setitem__'


def match_unary_operation(instr_name: str) -> str:
    if "NEGATIVE" in instr_name:
        return '__neg__'
    elif "NOT" in instr_name:
        return ''  # TO-DO: Add operation
    elif "INVERT" in instr_name:
        return '__invert__'

    return '__pos__'


def match_compare_operation(instr_name: str) -> str:
    if instr_name.__eq__('<'):
        return '__lt__'
    if instr_name.__eq__('<='):
        return '__le__'
    if instr_name.__eq__('!='):
        return '__ne__'
    if instr_name.__eq__('>'):
        return '__ge__'
    if instr_name.__eq__('>='):
        return '__gt__'

    return '__eq__'


def extend_possible_types(ref, index, possible_types):
    """

    :param ref:
    :param index: Refers to either direct or indirect reference
    :param possible_types:
    :return:
    """
    possible_types = list(possible_types)
    if len(ref['possible_types']) > index:
        # Probably a very ugly way to avoid repeating entries
        possible_types_set = set(ref['possible_types'][index])
        possible_types_set.update(possible_types)
        ref['possible_types'][index] = list(possible_types_set)
    else:
        ref['possible_types'].append(possible_types)


def update_reference_with_method(references, method_line, method_dict, builtin_method_types):
    for ref in references:
        possible_types = set()
        noted_method_calls = []

        # TO-DO: Fix the level system to take account of operations
        # For example, currently: x[0] = p0
        # will record the __setitem__ operation but with level 0
        # the data should record level 1 instead

        if match_parameter(ref['param'], method_line):
            noted_method_calls.append(method_dict)
            # The index number refers to the reference level
            possible_types.update(builtin_method_types)

            ref['method_calls'].extend(noted_method_calls)
            if len(noted_method_calls) > 0:
                # If it's another direct reference then just update the first list
                extend_possible_types(ref, 0, possible_types)
                continue

        # Don't judge my naming conventions, I already judge them
        for r in ref['refs']:
            if match_parameter(r, method_line):
                method_dict['level'] = 1  # Refers to an indirect parameter reference

                possible_types.update(builtin_method_types)
                noted_method_calls.append(method_dict)

                break

        ref['method_calls'].extend(noted_method_calls)
        if len(noted_method_calls) > 0:
            extend_possible_types(ref, 1, possible_types)


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

    _DATA_TYPE_OPERATIONS = {
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

    # Python Mapping Operators to Functions Table
    # (Provided by the Python documentation: https://docs.python.org/3/library/operator.html)
    _BINARY_OPERATORS = {
        '+': '__add__',
        '-': '__sub__',
        '*': '__mul__',
        '/': '__truediv__',
        '//': '__floordiv__',
        # TO-DO: Include bitwise AND: a & b
        '^': '__xor__',
        # TO-DO: Include bitwise OR: a | b
        '**': '__pow__',
        '<<': '__lshift__',
        '>>': '__rshift__',
        '%': '__mod__',
        # TO-DO: Include matmul: a @ b
    }

    def match_binary_operation(self, instr_argrepr: str):
        possible_types = []

        for sign, operation in self._BINARY_OPERATORS.items():
            if sign.__eq__(instr_argrepr):
                if type(operation) == list:
                    possible_types.extend(operation)
                else:
                    possible_types.append(operation)

        return possible_types

    def check_builtin_methods(self, method_name: str):
        possible_types = []
        method_name = method_name.lstrip().rstrip()

        # Check if the method can be found in the builtin methods
        # for the recorded data types
        for type_str, operations in self._DATA_TYPE_OPERATIONS.items():
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
        # local_variables = code.co_varnames[code.co_argcount:]
        # Get the names of all built-in/library methods that get called in the function
        method_calls = code.co_names

        # Record references to parameters
        for param_name in param_names:
            # Create a dictionary representing the parameter and its references
            parameter_info = {
                'param': param_name,
                'refs': [],
                'method_calls': [],
                'possible_types': []
            }
            # Add the parameter info to the list
            references.append(parameter_info)

        instructions = list(dis.get_instructions(code))
        possible_method_calls = []

        for instr in instructions:
            # print(instr)

            # TO-DO: CONTAINS_OP -> el in seq -> __contains__
            # IS_OP ->
            #   a is b -> is_(a,b)
            #   a is not b -> is_not(a, b)

            # STORE_SUBSCR -> a[index] = b  -> __setitem__
            # DELETE_SUBSCR -> del a[index] -> __delitem__
            # BINARY_SUBSCR -> a = b[index] -> __getitem__

            # COMPARE_OP ->
            #   a < b -> lt -> __lt__
            #   a <= b -> le -> __le__
            #   a == b -> eq -> __eq__
            #   a != b -> ne -> __ne__
            #   a > b -> ge -> __ge__
            #   a >= b -> gt -> __gt__

            # Get only operations that store value
            if instr.opname.startswith('STORE_') and instr.argval is not None:
                # Get the actual line of code (done after the if because negative indexes are a thing)
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                for ref in references:
                    if match_parameter(ref['param'], code_line):
                        ref_set = set(ref['refs'])  # dumb ass naming
                        ref_set.update(instr.argval)
                        ref['refs'] = list(ref_set)

            elif instr.opname.__contains__('_SUBSCR'):
                code_line = func_body[instr.positions.lineno - self._OFFSET]

                method_name = match_subscribe_operation(instr.opname)
                if method_name == '':
                    continue

                possible_method_calls.append({
                    'name': method_name,
                    'line': code_line.replace('\n', ''),
                })

            elif instr.opname.__eq__('LOAD_METHOD') and instr.argval is not None:
                if instr.argval in method_calls:
                    code_line = func_body[instr.positions.lineno - self._OFFSET]
                    possible_method_calls.append({
                        'name': instr.argval,
                        'line': code_line.replace('\n', ''),
                    })
            elif instr.opname.startswith('UNARY_'):
                code_line = func_body[instr.positions.lineno - self._OFFSET]

                method_name = match_unary_operation(instr.opname)
                if method_name == '':
                    continue

                possible_method_calls.append({
                    'name': method_name,
                    'line': code_line.replace('\n', ''),
                })

            # Handle BINARY_OP where the argepr = '+', '*'..
            elif instr.opname.__eq__('BINARY_OP') and instr.argrepr is not None:
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                method_names = self.match_binary_operation(instr.argrepr)
                if len(method_names) == 0:
                    continue

                for method_name in method_names:
                    possible_method_calls.append({
                        'name': method_name,
                        'line': code_line.replace('\n', ''),
                    })

            elif instr.opname.__eq__('COMPARE_OP') and instr.argval is not None:
                # TO-DO: Figure out if there's value in all this processing...
                # It could be the case that COMPARE_OP refer to every data type
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                method_name = match_compare_operation(instr.argval)

                possible_method_calls.append({
                    'name': method_name,
                    'line': code_line.replace('\n', ''),
                })

            elif instr.opname.__eq__('CONTAINS_OP'):
                code_line = func_body[instr.positions.lineno - self._OFFSET]
                possible_method_calls.append({
                    'name': '__contains__',
                    'line': code_line.replace('\n', ''),
                })

        # Check if any of the parameters have been used in a method call
        for method_info in possible_method_calls:
            method_name = method_info['name']
            method_line = method_info['line']

            builtin_method_types = self.check_builtin_methods(method_name)
            # No point in continuing if we cannot map the method
            if len(builtin_method_types) == 0:
                continue

            method_dict = make_method_dict(method_info, builtin_method_types)
            update_reference_with_method(references, method_line, method_dict, builtin_method_types)

        return references
