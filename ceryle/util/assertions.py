
def assert_type(value, *types):
    type_name_cache = []
    for t in types:
        if t is None:
            if value is None:
                return value
            type_name_cache.append(str(None))
            continue
        if not isinstance(t, type):
            raise TypeError(f'not a type; {t}')
        if isinstance(value, t):
            return value
        type_name_cache.append(t.__name__)
    types_str = ', '.join(type_name_cache)
    raise TypeError(f'not matched to any type {types_str}; actual: {type(value).__name__}')
