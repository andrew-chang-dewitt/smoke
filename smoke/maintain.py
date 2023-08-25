"""
The meat & potatoes of this program, the `maintain` function uses a given `Fan`
object & single `Probe` object to attempt to reach & maintain a given
temperature by controlling fan speed in response to the temperature readings
from the probe.

Example usage:

```
from smoke.fan import Fan
import smoke.maintain
from smoke.thermistor import Probes, Probe

fan = Fan(2)              # set up fan on GPIO pin 2
probes = Probes([1, 2])   # set up probes on MCP3008 channels 0 & 1
air = Probes.get_probe(1) # get the air temp probe on probe 1

maintain(107, air, fan)   # maintain an air temp of 107 C
                          # +/- the PRECISION constant
```
"""

from time import sleep
from typing import List, Self
from smoke.fan import Fan
from smoke.thermistor import Probe

SAMPLE_RATE = 10    # sample every 10 seconds
PRECISION = 5       # define a significant difference as 5 degrees Celsius
# define large, medium, & small temperature differences as order of magnitude,
# half an order, & the actual value based of the PRECISION constant
DIFFS = {
    "large": PRECISION * 10,
    "medium": PRECISION * 5,
    "small": PRECISION,
}
# define large, medium, & small temperature differences based off precision
# value as 10th, 100th, & 1000ths of the value per a second
TRENDS = {
    "large": PRECISION / 10,
    "medium": PRECISION / 100,
    "small": PRECISION / 1000,
}


# TODO: there might be a better built-in data structure for this
class NHistory:
    _values: List[float]
    _max: int

    def __init__(self, n: int) -> None:
        self._values = []
        self._max = n

    def push(self, value: float) -> Self:
        self._values.append(value)

        if len(self._values) > self._max:
            self._values.pop(0)

        return self

    def get_values(self) -> List[float]:
        return self._values


def find_trend(values: List[float]) -> float:
    """Find the trending rate of change for the given list of values."""
    # first find the relatively best fitting trend line in either linear,
    # quadratic, etc. from
    # then use derivatives of that line to find the slope at the newest
    # (last) point on the line
    # finally, return that slope value as a float
    raise NotImplementedError


def maintain(target: float, air: Probe, fan: Fan, food: Probe) -> None:
    """
    Attempts to maintain the given target temperature.

    Uses the given Probe & Fan objects to read the current temperature in a
    loop & control the fan speed accordingly.
    """
    # initialize an object for storing the last 10 minutes of temperature data
    history = NHistory(60)

    while True:
        # get current temp & push it onto the history
        current_temp = air.get_temp_c()
        history.push(current_temp)
        # determine the trending rate of change based on the history
        trend = find_trend(history.get_values())
        # determine how far off the current temp is from the target
        diff = target - current_temp

        # print status to stdout
        print(f'Air temp: {air}')
        print(f'Food temp: {food}')
        print(f'Diff: {diff}')
        print(f'Trend: {trend}')

        # if diff is significantly negative, turn off the fan
        if diff < (0 - PRECISION):
            fan.set_speed(0)

        # if diff is large, set fan sped to fastest
        elif diff > DIFFS["large"]:
            # and trend is small, set fan speed to fast
            if trend < TRENDS["small"]:
                fan.set_speed(3)
            # and trend is medium, set fan speed to medium
            if trend < TRENDS["medium"]:
                fan.set_speed(2)
            # and trend is large, set fan speed to slow
            if trend < TRENDS["large"]:
                fan.set_speed(1)

        # if diff is medium
        elif diff > DIFFS["medium"]:
            # and trend is small, set fan speed to medium
            if trend < TRENDS["small"]:
                fan.set_speed(2)
            # and trend is medium, set fan speed to slow
            if trend < TRENDS["medium"]:
                fan.set_speed(1)
            # and trend is large, set fan speed to off
            if trend < TRENDS["large"]:
                fan.set_speed(0)

        # if diff is small
            # and trend is small, set fan speed to slow
            if trend < TRENDS["small"]:
                fan.set_speed(1)
            # and trend is medium or large, set fan speed to off
            if trend < TRENDS["medium"]:
                fan.set_speed(0)

        # if diff is insignificant, do nothing

        # wait for 10 seconds & then repeat
        sleep(SAMPLE_RATE)
