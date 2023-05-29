import itertools


def grab_default_data(type_str: str):
    match type_str:
        case "str":
            return ''
        case "bool":
            return True
        case "dict":
            return {}
        case "int":
            return 0
        case "float":
            return 0.0
        case "complex":
            return 0j
        case "list":
            return []
        case "tuple":
            return ()
        case "range":
            return range(0)
        case "set":
            return set()
        case "frozenset":
            return frozenset()
    pass


def create_default_values(ref):
    default_values = []

    # TO-DO: The program could not figure out a type
    if len(ref['possible_types']) == 0:
        pass

    direct_ref = ref['possible_types'][0]
    indirect_ref = ref['possible_types'][1]

    # If there are direct reference guesses then we should just look at them
    if len(direct_ref) > 0:
        for type_str in direct_ref:
            default_values.append(grab_default_data(type_str))

    elif len(indirect_ref) > 0:
        for type_str in indirect_ref:
            default_values.append(grab_default_data(type_str))

    return default_values


class Generator:

    def __init__(self, func_name):
        self.func_name = func_name
        self.possible_param_values = []

    def consume(self, reference_obj, param_num):
        values_array = []
        possible_param_values_set = set()

        for i in range(len(reference_obj)):
            ref = reference_obj[i]
            values_array.append(create_default_values(ref))

            # param0 -> str, int
            # param0 -> ['', 0]

            for j in range(i, len(reference_obj) - 1):
                ref_next = reference_obj[j]
                values_array.append(create_default_values(ref_next))

                # param1 -> list, int
                # param1 -> [[], 0]

        for value in itertools.permutations(values_array, param_num):
            value_str = f'{self.func_name}('
            for elem in value:
                if elem[0] == '':
                    value_str += '"", '
                else:
                    value_str += f'{elem[0]}, '

            value_str = value_str.rstrip()[:-1] + ")"

            # TO-DO: Compile the value_str before adding it to the set

            possible_param_values_set.add(value_str)

            # solution -> [
            #   "'', []",
            #   "'', 0",
            #   "0, []",
            #   "0, 0"
            # ]

        self.possible_param_values = list(possible_param_values_set)
