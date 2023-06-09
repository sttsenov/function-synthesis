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
    return re.search(rf"\b(?=\w){param_name}\b(?![\w'\"])(?!( +')+)(?!( +\")+)", line)


def check_method_takes_args(method_name: str, code_line: str):
    return not code_line.split(method_name)[-1].startswith('()')


def grab_argval(code_line: str):
    # TO-DO: Check how this works when unpacking values: x, y = y, x
    # Removes square brackets
    return code_line.split('=')[0].strip().split('[')[0]


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
        # Exclusion that makes sure that types that would cause an exception get removed
        # For example:
        #   p0 = 5 + 10 -> will note an int data type for "p0"
        #   p0[1:3] -> will note a sequence data type for "p0"
        #   In this case these two might be mutually exclusive
        possible_types_set = set(ref['possible_types'][index])
        possible_types_set = possible_types_set.intersection(possible_types)
        ref['possible_types'][index] = list(possible_types_set)
    else:
        ref['possible_types'].append(possible_types)


def update_parameter_references(references, method_line, argument, match_param_field='param'):
    # Go through the parameters
    for ref in references:

        if argument == ref['param']:
            return

        # Check if we are checking for direct or indirect references: 'param' or 'refs'
        if match_param_field == 'refs':
            should_stop = False
            ref_set = set()

            # Generate a set of all recorded references
            for r in ref['refs']:
                ref_set.update(r)

            # Iterate through the levels of indirect references
            for level_index in range(len(ref['refs'])):
                # Grab the recorded references for the current level
                recorded_level = ref['refs'][level_index]

                # Early stopping if an argument has been recorded
                if argument in ref_set:
                    break

                # Iterate through the recorded values
                for val in recorded_level:
                    # Check for match
                    if match_parameter(val, method_line):
                        # If new level of referencing has been recorded
                        # then update the next level with the new argument
                        if level_index + 1 < len(ref['refs']):
                            next_level = level_index + 1
                            r_set = set(ref['refs'][next_level])
                            r_set.update(argument)
                            ref['refs'][next_level] = list(r_set)

                        # Check if we are on the last recorded level
                        # and create a new level
                        if len(ref['refs']) == level_index + 1:
                            ref['refs'].append([argument])

                        should_stop = True
                        break

                # Stop iterating and recording
                if should_stop:
                    break

        # Looking at the first level of indirect references that refer to the parameters
        elif match_param_field == 'param' and match_parameter(ref['param'], method_line):
            # Check if an indirect level reference already exists
            # if so append the argument to it
            curr_level = 0

            if len(ref['refs']) > curr_level:
                ref_set = set(ref['refs'][curr_level])
                ref_set.update(argument)
                ref['refs'][curr_level] = list(ref_set)

            # Create a new reference level and store the argument
            else:
                ref_set = set(ref['refs'])
                ref_set.update(argument)
                ref['refs'].append(list(ref_set))

    # Checks if 'refs' field has been computed
    if match_param_field == 'refs':
        return
    update_parameter_references(references, method_line, argument, 'refs')


def update_reference_with_method(references, method_line, method_dict, builtin_method_types):
    for ref in references:
        possible_types = set()
        noted_method_calls = []

        if match_parameter(ref['param'], method_line):
            noted_method_calls.append(method_dict)
            # The index number refers to the reference level
            possible_types.update(builtin_method_types)

            ref['method_calls'].extend(noted_method_calls)
            if len(noted_method_calls) > 0:
                # If it's another direct reference then just update the first list
                extend_possible_types(ref, 0, possible_types)
                continue

        should_stop = False
        # Don't judge my naming conventions, I already judge them
        for curr_level in range(len(ref['refs'])):
            r = ref['refs'][curr_level]
            # Doesn't everyone love nested loops....
            for var in r:
                if match_parameter(var, method_line):
                    method_dict['level'] = curr_level + 1  # Refers to an indirect parameter reference

                    possible_types.update(builtin_method_types)
                    noted_method_calls.append(method_dict)

                    should_stop = True
                    break

            if should_stop:
                break

        ref['method_calls'].extend(noted_method_calls)
        if len(noted_method_calls) > 0:
            extend_possible_types(ref, 1, possible_types)


class OperatorClass:
    _OFFSET = 3
    _SUBSCR_REGEX = re.compile(r'\w+\[[\w:]+]')

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
        method_name = method_name.strip()

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

        # TO-DO: Eventually work on dealing with type hints, args and kwargs...
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
            print(instr)

            # CONTAINS_OP -> el in seq -> __contains__

            # TO-DO: IS_OP ->
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
            # NOTE: Store operations should be treated independently
            if instr.opname.startswith('STORE_'):
                # print(instr)
                # Get the actual line of code (done after the if because negative indexes are a thing)
                code_line = func_body[instr.positions.lineno - self._OFFSET]

                argument = instr.argval
                # Handle operations like STORE_SUBSCR
                if argument is None:
                    argument = grab_argval(code_line)

                print(f'Argument: {argument}')
                update_parameter_references(references, code_line, argument)

            if instr.opname.__contains__('_SUBSCR'):
                # print(instr)
                code_line = func_body[instr.positions.lineno - self._OFFSET].replace('\n', '')
                # Breakdown the line based on the offset of the operation
                operation_partition = code_line[:instr.positions.col_offset]

                # Finds the index of the last square brackets that should be included
                start_index = operation_partition.rfind('[')
                end_index = code_line[start_index:].find(']') + (start_index + 1)

                operation_partition = code_line[:end_index]
                variable_call = self._SUBSCR_REGEX.findall(operation_partition)[-1]

                # TO-DO: Decide whether I should introduce new field in the method_info dictionary that notes
                # that the algorithm is dealing with a subscription operator

                # Benefit: That will get to record the line of code and not just the sector from that line
                # Drawback: Will require more processing power for three types of operators
                method_name = match_subscribe_operation(instr.opname)
                if method_name == '':
                    continue

                possible_method_calls.append({
                    'name': method_name,
                    'line': variable_call,
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
