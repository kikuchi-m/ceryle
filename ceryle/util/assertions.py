
def assert_type(value, value_type):
    if not isinstance(value_type, type):
        raise TypeError(f'2nd argument must be a type; passed {type(value_type)}')
    if not isinstance(value, value_type):
        raise TypeError(f'not matched to type {value_type.__name__}; actual: {type(value).__name__}')
