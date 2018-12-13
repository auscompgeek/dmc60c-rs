import re

RUST_TYPES = {
    'short': 'i16',
    'unsigned short': 'u16',
    'int': 'i32',
    'uint32_t': 'u32',
    'unsigned int': 'u32',
    'double': 'f64',
    'float': 'f32',
}

RUST_CONSTRUCTOR_NAMES = ['new', 'with_wheel']


def to_snake_case(s: str) -> str:
    return re.sub(r'(?<=[a-z0-9])[A-Z]|(?!^|_)[A-Z](?=[a-z])', r'_\g<0>', s).lower()


def method_hook(fn, data):
    snake_name = to_snake_case(fn['name'])

    in_params = []

    for i, p in enumerate(fn['parameters']):
        p['snake_name'] = to_snake_case(p['name'] or f'param{i}')
        rust_type = RUST_TYPES.get(p['raw_type'], p['raw_type'])
        if p['array']:
            if 'array_size' in p:
                rust_type = f"[{rust_type}; {p['array_size']}]"
            else:
                # dummy
                rust_type = f"[{rust_type}]"

        p['rust_type'] = qual_rust_type = rust_type
        p['rust_decl'] = f"{p['snake_name']}: {p['rust_type']}"

        in_params.append(p)
        p['qual_rust_type'] = qual_rust_type

    return_type = fn['rtnType']
    if return_type != 'void':
        return_type = RUST_TYPES.get(return_type, return_type)
        fn['rust_returns'] = return_type
    else:
        fn['rust_returns'] = None

    fn['in_params'] = in_params

    fn['getter'] = snake_name.startswith(('get_', 'is_'))
    if snake_name.startswith('get_') and not in_params:
        snake_name = snake_name[4:]

    if fn['constructor']:
        fn['rust_returns'] = 'Self'
    else:
        fn['rust_name'] = snake_name

    fn['rustdoc'] = ''  # TODO


def class_hook(cls, data):
    constructor_idx = 0
    for fn in cls['methods']['public']:
        if fn['constructor']:
            fn['rust_name'] = RUST_CONSTRUCTOR_NAMES[constructor_idx]
            constructor_idx += 1
            fn['constructor_idx'] = constructor_idx
