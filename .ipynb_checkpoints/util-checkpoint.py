import math


def round_f(n, decimals, agg):
    if decimals < 0:
        raise ZeroDivisionError()

    factor = 10**decimals

    if agg == 'floor':
        return math.floor(n * factor) / factor
    elif agg == 'ceil':
        return math.ceil(n * factor) / factor
    else:
        raise ValueError("Aggregate function must be only ceil or floor.")