
def assert_type(value, *types):
    type_name_cache = []
    for t in types:
        if not isinstance(t, type):
            raise TypeError(f'not a type; {t}')
        if isinstance(value, types):
            return value
        type_name_cache.append(t.__name__)
    types_str = ', '.join(type_name_cache)
    raise TypeError(f'not matched to any type {types_str}; actual: {type(value).__name__}')
