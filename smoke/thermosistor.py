"""
Tools for using NTC thermosistor probes w/ Raspberry Pi GPIO & MCP3008 ADC.

Assumes you have each probe wired up with a fixed 100k 5% resistor and
corresponding to on of 8 channels on the MCP3008 chip.

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

    def __init__(
        self,
        probe_nums: List[int],
        cs: digitalio.DigitalInOut,
        spi: busio.SPI,
        mcp: MCP.MCP3008,
        max_probes: int = 8
    ):
        self._channels = [None]*max_probes
        self._cs = cs
        self._spi = spi
        self._mcp = mcp

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

    @staticmethod
    def _check_valid_probe_num(num: int) -> None:
        if num < 1 or num > 8:
            raise IndexError(
                f'Probe number {num} is invalid. ' +
                'Please specify probes only as numbers 1 through 8.')

    def __str__(self) -> str:
        """Get newline-separated list of current temps by probe number."""
        output_list: List[str] = []

        for idx, channel in enumerate(self._channels):
            if channel is not None:
                res = resistance(channel.value)
                temp = steinhart_temperature_c(res)
                output_list.append(f'Probe {idx + 1}: {temp}')

        return "\n".join(output_list)


def setup_probes(probes: List[int]) -> Probes:
    """
    Set up thermosistor circuitry for the given probes.

    Specify which probes are connected using a list of numbers 1 through 8.
    e.g. if probes 1 & 3 are connected, use

    ```
    setup_probes([1,3])
    ```
    """
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)

    return Probes(probes, cs, spi, mcp)


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
