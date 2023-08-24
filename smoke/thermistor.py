r"""
Tools for using NTC thermistor probes w/ Raspberry Pi GPIO & MCP3008 ADC.

Assumes you have each probe wired up with a fixed 100k 5% resistor and
corresponding to one of 8 channels on the MCP3008 chip.

Initialize the board by calling the `setup_probes` method. You can specify the
probes to use at call time or by adding and/or removing probes later:

```
probes = setup_probes([1])  # sets up the board with only the first probe
probes.add_probe(2)         # now probes 1 & 2 are turned on
probes.add_probe(4)         # now probes 1, 2, & 4 are turned on
probes.remove_probe(2)      # now only probes 1 & 4 are turned on
```

Get a string representing the current temp of each probe by using the built-in
__str__ method:

```
print(f'Current temps:\n{probes}')
# outputs something like:
# Current temps:
# Probe 1: 35.5 C
# Probe 4: 95.2 C
```

You can also get a list of all the current temps (indexed by probe number - 1)
with None representing probes that are turned off with `Probes.temps()`:

```
probes.temps() => [35.5, None, None, 95.2, None, None, None, None]
```
"""

import math
from typing import List, Optional, Self

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio
import board
import busio

FIXED_RESISTOR = 100000.0
PROBES = MCP.P0, MCP.P1, MCP.P2, MCP.P3, MCP.P4, MCP.P5, MCP.P6, MCP.P7


class Probes:
    """
    An object representing all available probes.

    Specify which probes are available at creation by passing a list of probe
    numbers 1 through 8. For example:

    ```
    probes = Probes([1,3])
    ```

    means probes 1 & 3 are available while 2, 4, 5, 6, 7, & 8 are not.
    """

    _channels: List[Optional[AnalogIn]]
    _cs: digitalio.DigitalInOut
    _spi: busio.SPI
    _mcp: MCP.MCP3008
    _max_probes: int

    def __init__(
        self,
        probe_nums: List[int],
        max_probes: int = 8
    ):
        """
        Set up thermistor circuitry for the given probes.

        Specify which probes are connected using a list of numbers 1 through 8.
        e.g. if probes 1 & 3 are connected, use

        ```
        Probes([1,3])
        ```
        """
        self._channels = [None]*max_probes
        self._spi = busio.SPI(
            clock=board.SCK,
            MISO=board.MISO,
            MOSI=board.MOSI)
        self._cs = digitalio.DigitalInOut(board.D5)
        self._mcp = MCP.MCP3008(self._spi, self._cs)
        self._max_probes = max_probes

        for probe in probe_nums:
            self.add_probe(probe)

    def add_probe(self, num: int) -> Self:
        """Initialize probe for given number."""
        self._check_valid_probe_num(num)
        index = num - 1
        self._channels[index] = AnalogIn(self._mcp, PROBES[index])

        return self

    def remove_probe(self, num: int) -> Self:
        """Remove probe for given number."""
        self._check_valid_probe_num(num)
        self._channels[num - 1] = None

        return self

    def _check_valid_probe_num(self, num: int) -> None:
        if num < 1 or num > self._max_probes:
            raise IndexError(
                f'Probe number {num} is invalid. ' +
                'Please specify probes only as numbers 1 through ' +
                f'{self._max_probes}.')

    def temps(self) -> List[Optional[float]]:
        """
        Get current temps for all probes.

        Temps are represented in Celsius as floats w/ uninitialized probes as
        None.
        """
        output: List[Optional[float]] = [None]*self._max_probes

        for idx, channel in enumerate(self._channels):
            if channel is not None:
                res = resistance(channel.value)
                temp = steinhart_temperature_c(res)
                output[idx] = temp

        return output

    def __str__(self) -> str:
        """Get newline-separated list of current temps by probe number."""
        output_list: List[str] = []

        for idx, temp in enumerate(self.temps()):
            if temp is not None:
                output_list.append(f'Probe {idx}: {temp}')

        return "\n".join(output_list)


def steinhart_temperature_c(
    input_resistance: float,
    fixed_resistor: float = FIXED_RESISTOR,
    nominal_resistance: float = 25.0,
    beta: float = 3950.0
) -> float:
    """Get temperature from given input_resistance using Steinhart-Hart."""
    # log(input_resistance/fixed_resistor) / beta
    steinhart = math.log(input_resistance / fixed_resistor) / beta
    # log(input_resistance/fixed_resistor) / beta + 1/nominal_resistance
    steinhart += 1.0 / (nominal_resistance + 273.15)
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart


def resistance(value: int) -> float:
    """Get resistance from input ADC value."""
    num: float = FIXED_RESISTOR
    den: float = 65535/value - 1
    return num/den
