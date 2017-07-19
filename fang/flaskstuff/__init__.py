def func_compare(argument, standard_value, compare_value):
    compare_operator = {
        '<=': compare_lessorequal,
        '>=': compare_largerorequal,
        '=': compare_equal,
        '>': compare_larger,
        '<': compare_lessthan,
        '<>': compare_notequal,
        '&': compare_final_equal,
        '|': compare_final_or,
        'contains': compare_contants
    }
    func = compare_operator.get(argument)
    return func(standard_value, compare_value)


def compare_contants(standard_value=None, compare_value=None):  # compare check string in
    return standard_value in compare_value


def compare_lessorequal(standard_value=None, compare_value=None):  # compare int
    return compare_value <= standard_value


def compare_largerorequal(standard_value=None, compare_value=None):  # compare int
    return compare_value >= standard_value


def compare_equal(standard_value=None, compare_value=None):  # compare int
    return compare_value == standard_value


def compare_larger(standard_value=None, compare_value=None):  # compare int
    return compare_value > standard_value


def compare_lessthan(standard_value=None, compare_value=None):  # compare int
    return compare_value < standard_value


def compare_notequal(standard_value=None, compare_value=None):  # compare int
    return compare_value != standard_value


def compare_final_equal(output_value=None, output_value_=None):  # compare true or false
    return output_value == output_value_


def compare_final_or(output_value=None, output_value_=None):  # compare true or false
    return output_value == output_value_