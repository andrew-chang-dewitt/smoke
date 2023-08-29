from re import L
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

    for i, value in enumerate(values[1:]):
        x, y = value
        x_prev, y_prev = values[i - 1]
        delta_x = x - x_prev
        delta_y = y - y_prev
        delta_xs.append(delta_x)
        delta_ys.append(delta_y)

    avg_delta_y: float = sum(delta_ys)/length
    avg_delta_x: float = sum(delta_xs)/length

    return avg_delta_y/avg_delta_x


def nonlinear_regression_slope(values: List[Tuple[ (float, float) ]]) -> float:
    """Find the slope at the last value for a given set of values."""
    # first find the relatively best fitting trend line in either linear,
    # quadratic, etc. from
    # then use derivatives of that line to find the slope at the newest
    # (last) point on the line
    # finally, return that slope value as a float

    raise NotImplementedError
