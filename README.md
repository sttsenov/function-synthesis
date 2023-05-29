# Parameter Type Matcher

Parameter Type Matcher is a side-project that aims to programmatically determine
the data type of all the parameters that are noted in a function definition. The
idea for this project came from my Bachelor's Thesis which focused on the generation
of synthetic data for Python classes.

## Installation

This project is not current added as a package and need to be pulled from the repository.
The code can be easily executed from any IDE by running the **param_match.py**

## Examples

As seen in the **param_match.py** there is a test docstring containing a function:
```python
def test(p0, p1):
    # Records a reference to a parameter/s
    x = p0 * p1

    # Used to verify that only type specific methods get recorded
    print(p0)

    # Calls type specific methods
    p0.upper()
    return x.startswith('1')
```

Executing the project creates a JSON breakdown of the this function that looks like this:
![JSON Breakdown of function](/screenshots/func_breakdown.png "Function Breakdown")

## Current Limitations

Currently this project doesn't have a good way to create connections between parameters.
For example ```x = p0 * p1``` means that local variable **x** refers to both parameters
but that doesn't necessarily mean that it can be used to guess the type of both parameters.

Another limitation is that the project can only record a direct reference to a parameter.
Meaning that a line like: ```y = x.startswith('...')``` will not be recorded.