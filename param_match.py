import json
from helpers import log
from parameter_matcher.generator import Generator
from type_operations import OperatorClass

_EXCEPTION_TEMPLATE = "An exception of type {0} occurred. Arguments:\n{1!r}"

TEST = """
def function(p0, p1):
    x = p0 + [10]
    p0[0] = 3
    z = p0[0] + 5
    y = p1.startswith('a')

    return y / x
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
            # if line != '':
            func_body.append(line + '\n')

    breakdown["body"] = func_body
    return breakdown


def match_parameters(input_str):
    _globals = {}

    # Compile the provided function
    compiler = compile(input_str, '', 'exec')
    exec(compiler, _globals)

    operator = OperatorClass()
    breakdown = breakdown_func(input_str)
    func_object = _globals[breakdown["name"]]
    #
    # print(f'NAME: {breakdown["name"]}')
    # print(f'PARAMS: {breakdown["params"]}')
    # print(f'FUNC BODY: {breakdown["body"]}')
    #
    # print('---------------------------------------------')
    # print(f'Function object: {func_object}')
    # print(f'Function methods: {dir(func_object)}')
    # print('---------------------------------------------')

    generator = Generator(breakdown["name"])
    references = operator.record_references(func_object, breakdown["body"])

    f_data = json.dumps(references, indent=4)
    # Write to file
    with open('files/func_breakdown.json', 'w') as fp:
        fp.write(f_data)

    # Create function execution options
    generator.consume(references)

    possible_method_calls = generator.possible_method_calls
    method_calls = []

    for method in possible_method_calls:
        method_str = input_str + f'\n{method}'
        log('INFO', f'Executing with: {method}')

        try:
            compiler = compile(method_str, '', 'exec')
            exec(compiler)

            method_calls.append(method)
            log('SUCCESS', f'Execution successful.')

        except Exception as e:
            # TO-DO: Have a look at adding method_calls even when an IndexError happens
            message = _EXCEPTION_TEMPLATE.format(type(e).__name__, e.args)
            log('ERROR', message)

        log('INFO', f'Finished Execution with: {method}')

    print(f'Possible Method Calls: {possible_method_calls}')
    print(f'Actual Method Calls: {method_calls}')
    print(f'Len Actual Method Calls: {len(method_calls)}')

    # print('---------------------------------------------')
    #
    # for ref in references:
    #     print(f'Param name: {ref["param"]}')
    #     print(f'Reference variables: {ref["refs"]}')
    #     for method in ref["method_calls"]:
    #         print('---------------------------------------------')
    #
    #         print(f'Method name: {method["method"]["name"]}')
    #         print(f'Code line: {method["method"]["line"]}')
    #         print(f'Possible data types: {method["possible_types"]}')
    #         print(f'Takes arguments: {method["takes_arguments"]}')
    #         print(f'Level of reference (0 -> direct, 1 -> indirect): {method["level"]}')
    #
    #         print('---------------------------------------------')


if __name__ == "__main__":
    match_parameters(TEST)
