from statistics import fmean
from typing import List, Tuple


def find_trend(y_values: List[float], delta_x: float) -> float:
    """Find the trending rate of change for the given list of values."""

    return simple_slope([
        (0 + (delta_x * i), y)
        for i, y in enumerate(y_values)])


def simple_slope(values: List[Tuple[(float, float)]]) -> float:
    """Find the trending rate of change using a simple heuristic."""
    length = len(values) - 1

    # guard against DivisionByZeroError
    if length < 1:
        return 0.0

    delta_ys: List[float] = []
    delta_xs: List[float] = []
    y_values: List[float] = []

    for i, value in enumerate(values[1:]):
        x_now, y_now = value
        x_prev, y_prev = values[i]

        delta_xs.append(x_now - x_prev)
        delta_ys.append(y_now - y_prev)
        y_values.append(y_prev)

    y_values.append(values[-1][1])

    avg_delta_y: float = sum(delta_ys)/length
    avg_delta_x: float = sum(delta_xs)/length
    avg_slope = avg_delta_y/avg_delta_x

    avg_y = fmean(y_values)
    variance_y = sum([(val_y - avg_y)**2 for val_y in y_values])/length

    return avg_slope * (1 + (variance_y/100))


def nonlinear_regression_slope(values: List[Tuple[ (float, float) ]]) -> float:
    """Find the slope at the last value for a given set of values."""
    # first find the relatively best fitting trend line in either linear,
    # quadratic, etc. from
    # then use derivatives of that line to find the slope at the newest
    # (last) point on the line
    # finally, return that slope value as a float

    raise NotImplementedError
