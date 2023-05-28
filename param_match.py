from type_operations import OperatorClass

TEST = """
def test(p0, p1):
    x = p0 * p1
    print(p0)
    print(p1)
"""


def breakdown_func(input_str: str):
    breakdown = {}
    is_body = False
    func_body = []

    for line in input_str.split('\n'):
        if "def" in line:
            line = line.split("(")  # def test(p0, p1, p2) -> ['def test', 'p0, p1, p2)']
            breakdown["name"] = line[0].split(" ")[-1]  # 'def test' -> 'test'
            # Removes the closing bracket
            line = line[1].split(")")[0]
            # Checks for multiple params
            if "," in line:
                # p0, p1, p2) -> p0, p1, p2 -> ['p0', 'p1', 'p2']
                breakdown["params"] = [param.lstrip().rstrip() for param in line.split(",")]
            else:
                # p0) -> p0
                breakdown["params"] = [line.lstrip().rstrip()]
            is_body = True
        elif is_body:
            line = line.lstrip().rstrip()
            if line is not '':
                func_body.append(line + '\n')

    breakdown["body"] = func_body
    return breakdown


def match_parameters(input_str):
    _globals = {}

    # Compile the provided function
    compiler = compile(input_str, '', 'exec')
    exec(compiler, _globals)

    # Create function execution options
    func_examples = """test(0, 0)"""

    operator = OperatorClass()
    breakdown = breakdown_func(input_str)
    func_object = _globals[breakdown["name"]]

    print(f'NAME: {breakdown["name"]}')
    print(f'PARAMS: {breakdown["params"]}')
    print(f'FUNC BODY: {breakdown["body"]}')

    print('---------------------------------------------')
    print(f'Function object: {func_object}')
    print(f'Function methods: {dir(func_object)}')
    print('---------------------------------------------')

    references = operator.record_references(func_object, breakdown["body"])
    for ref in references:
        print(f'{ref}')


if __name__ == "__main__":
    match_parameters(TEST)


