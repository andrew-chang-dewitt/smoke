"""
A module for controlling a PWM-enabled fan via GPIO.

Set up a fan object using the `Fan` class & specify the PWM pin number
(BCM mode) at initialization. Then control the speed (or turn it off entirely)
using the provided methods, `Fan.set_speed` & `Fan.off`.

```
fan = Fan(2)
fan.set_speed(1)    # set speed to slowest setting
fan.set_speed(2)    # set speed to medium setting
fan.set_speed(3)    # set speed to fastest setting
fan.set_speed(0)    # turn fan off
```
"""

from typing import Self
import RPi.GPIO as IO

# map speed ints to PWM duty cycles
SPEEDS = [0, 35, 65, 90]


class Fan:
    """
    The fan object class.

    Set up a fan object using the `Fan` class & specify the PWM pin number
    (BCM mode) at initialization. Then control the speed (or turn it off
    entirely) using the provided methods, `Fan.set_speed` & `Fan.off`.

    ```
    fan = Fan(2)
    fan.set_speed(1)    # set speed to slowest setting
    fan.set_speed(2)    # set speed to medium setting
    fan.set_speed(3)    # set speed to fastest setting
    fan.off()           # turn fan off
    ```
    """

    _fan: IO.PWM

    def __init__(self, pin: int) -> None:
        """Initialize a fan object with the given PWM pin."""
        IO.cleanup()
        IO.setmode(IO.BCM)
        IO.setup(pin, IO.OUT)
        self._fan = IO.PWM(pin, 100)
        self._fan.start(0)

    def set_speed(self, speed: int) -> None:
        """Set the speed to 0, 1, 2, or 3 where 0 is off & 3 is fastest."""
        try:
            self._fan.ChangeDutyCycle(SPEEDS[speed])
        except IndexError:
            raise IndexError(f'Speed {speed} is invalid, please provide a ' +
                             'number from 0 to 4.')

    def __enter__(self) -> Self:
        return self

    def __exit__(self) -> None:
        self._fan.stop()
        IO.cleanup()
