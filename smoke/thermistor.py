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
from typing import Dict, List, Optional, Self

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio
import board
import busio

FIXED_RESISTOR = 100000.0
PROBES = MCP.P0, MCP.P1, MCP.P2, MCP.P3, MCP.P4, MCP.P5, MCP.P6, MCP.P7


class Probe:
    """
    An object representing a single probe.

    Used to get the temperature reading of that probe as a float or string in
    Celsius or Fahrenheit.
    """

    _channel: AnalogIn
    _num: int
    _name: Optional[str]

    def __init__(self, mcp: MCP.MCP3008, channel: int) -> None:
        """Initialize a probe on the given MCP3008 data channel."""
        self._channel = AnalogIn(mcp, PROBES[channel])
        self._num = channel + 1
        self._name = None

    def get_temp_c(self) -> float:
        """Get the current temperature of the probe in Celsius."""
        res = resistance(self._channel.value)

        return steinhart_temperature_c(res)

    def set_name(self, name: str) -> None:
        """Set the probe's name as the given string."""
        self._name = name

    def get_name(self) -> Optional[str]:
        """Get the probe's name."""
        return self._name

    def unset_name(self) -> None:
        """Unname the probe."""
        self._name = None

    def get_identifier(self) -> str:
        """Get the probe's name, or number if it doesn't have one."""
        return self._name if self._name is not None else str(self._num)

    def __str__(self) -> str:
        """Render the current temperature of the probe as a string."""
        prefix = f'{self._name} [{self._num}]' \
            if self._name is not None \
            else f'Probe {self._num}'

        return f'{prefix}: {self.get_temp_c()}'


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

    _air_probe: Optional[int]
    _cs: digitalio.DigitalInOut
    _probes: List[Optional[Probe]]
    _max_probes: int
    _mcp: MCP.MCP3008
    _spi: busio.SPI
    _target_probe: Optional[int]

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
        self._probes = [None]*max_probes
        self._spi = busio.SPI(
            clock=board.SCK,
            MISO=board.MISO,
            MOSI=board.MOSI)
        self._cs = digitalio.DigitalInOut(board.D5)
        self._mcp = MCP.MCP3008(self._spi, self._cs)
        self._max_probes = max_probes
        self._air_probe = None
        self._target_probe = None

        for probe in probe_nums:
            self.add_probe(probe)

    def add_probe(self, num: int) -> Self:
        """Initialize probe for given number."""
        self._check_valid_probe_num(num)
        index = num - 1
        self._probes[index] = Probe(self._mcp, index)

        return self

    def get_probe(self, num: int) -> Optional[Probe]:
        """
        Get the probe object a given channel number.

        Returns None if probe is not initialized, otherwise returns the Probe.
        """
        self._check_valid_probe_num(num)

        return self._probes[num - 1]

    def remove_probe(self, num: int) -> Self:
        """Remove probe for given number."""
        self._check_valid_probe_num(num)
        self._probes[num - 1] = None

        return self

    def set_air_probe(self, num: int) -> Self:
        """Set the probe at the given number as the air temperature probe."""
        self._check_valid_probe_num(num)

        if self.get_probe(num) is None:
            raise ValueError(f'Probe number {num} is not set up. ' +
                             'Please set it up or try a different probe.')

        if self._target_probe == num:
            raise ValueError(f'Probe number {num} is already in ' +
                             'use as the target food probe.')

        self._air_probe = num
        probe = self.get_probe(num)

        if probe is not None:
            probe.set_name("Air")

        return self

    def unset_air_probe(self) -> Self:
        """Unset the probe currently designated as the air probe."""
        if self._air_probe is not None:
            probe = self.get_air_probe()

            if probe is not None:
                probe.unset_name()

            self._air_probe = None

        return self

    def get_air_probe(self) -> Optional[Probe]:
        """Get the air Probe object or raise an exception if it is not set."""
        if self._air_probe is None:
            raise ValueError("Air probe is not yet set.")

        return self.get_probe(self._air_probe)

    def set_target_probe(self, num: int) -> Self:
        """Set probe at the given number as the target temperature probe."""
        self._check_valid_probe_num(num)

        if self.get_probe(num) is None:
            raise ValueError(f'Probe number {num} is not set up. ' +
                             'Please set it up or try a different probe.')

        if self._air_probe == num:
            raise ValueError(f'Probe number {num} is already in ' +
                             'use as the air probe.')

        self._target_probe = num
        probe = self.get_probe(num)

        if probe is not None:
            probe.set_name("Food")

        return self

    def unset_target_probe(self) -> Self:
        """Unset the probe currently designated as the target probe."""
        if self._target_probe is not None:
            probe = self.get_target_probe()
            
            if probe is not None:
                probe.unset_name()

            self._target_probe = None

        return self

    def get_target_probe(self) -> Optional[Probe]:
        """
        Get the food target Probe object.

        Raises an exception if it is not set yet.
        """
        if self._target_probe is None:
            raise ValueError("Target probe is not yet set.")

        return self.get_probe(self._target_probe)

    def temps(self) -> Dict[str, Optional[float]]:
        """
        Get current temps for all probes.

        Temps are represented in Celsius as floats w/ uninitialized probes as
        None.
        """
        output: Dict[str, Optional[float]] = {}

        for idx, probe in enumerate(self._probes):
            if probe is None:
                output[str(idx)] = None
            else:
                output[probe.get_identifier()] = probe.get_temp_c()

        return output

    def _check_valid_probe_num(self, num: int) -> None:
        if num < 1 or num > self._max_probes:
            raise IndexError(
                f'Probe number {num} is invalid. ' +
                'Please specify probes only as numbers 1 through ' +
                f'{self._max_probes}.')

    def __str__(self) -> str:
        """Get newline-separated list of current temps by probe number."""
        output_list: List[str] = []

        for probe in self._probes:
            if probe is not None:
                output_list.append(str(probe))

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
