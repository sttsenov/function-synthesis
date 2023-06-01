import itertools
from helpers import log


class Generator:
    _DEFAULT_DATA = {
        'str': '',
        'bool': True,
        'dict': {},

        'int': 1,
        'float': 0.1,
        'complex': 1j,

        'list': [],
        'tuple': (),
        'range': range(0),

        'set': set(),
        'frozenset': frozenset()
    }

    def __init__(self, func_name):
        self.func_name = func_name
        self.possible_method_calls = []

    def grab_default_data(self, type_str: str, include_all=False):
        if include_all:
            return list(self._DEFAULT_DATA.values())

        for key, value in self._DEFAULT_DATA.items():
            if type_str.__eq__(key):
                return value
        pass

    def create_default_values(self, ref):
        default_values = []

        # The program could not figure out a type, so it grab all values
        if len(ref['possible_types']) == 0:
            return self.grab_default_data('', include_all=True)

        direct_ref = ref['possible_types'][0]

        # If there are direct reference guesses then we should just look at them
        if len(direct_ref) > 0:
            for type_str in direct_ref:
                default_values.append(self.grab_default_data(type_str))
        # Check if there are indirect references
        elif len(ref['possible_types']) > 1:
            indirect_ref = ref['possible_types'][1]
            for type_str in indirect_ref:
                default_values.append(self.grab_default_data(type_str))

        return default_values

    def consume(self, reference_obj):
        values_array = []
        possible_method_calls_set = set()

        for i in range(len(reference_obj)):
            ref = reference_obj[i]
            values_array.append(self.create_default_values(ref))

        print(f'Values Array: {values_array}')
        for value in list(itertools.product(*values_array)):
            value_str = f'{self.func_name}('
            for elem in value:
                if elem == '':
                    value_str += '"", '
                else:
                    value_str += f'{elem}, '

            value_str = value_str.rstrip()[:-1] + ")"
            possible_method_calls_set.add(value_str)

            # solution -> [
            #   "'', []",
            #   "'', 0",
            #   "0, []",
            #   "0, 0"
            # ]

        self.possible_method_calls = list(possible_method_calls_set)
