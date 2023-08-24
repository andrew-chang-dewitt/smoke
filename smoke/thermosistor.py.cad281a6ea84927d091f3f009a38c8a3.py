import math

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio
import board
import busio

FIXED_RESISTOR = 100000.0

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
channel = AnalogIn(mcp, MCP.P0)


def steinhart_temperature_C(r, Ro=FIXED_RESISTOR, To=25.0, beta=3950.0):
    steinhart = math.log(r / Ro) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart


def resistance(value: int) -> float:
    num: float = FIXED_RESISTOR
    den: float = 65535/value - 1
    return num/den


print(f'Raw ADC Value: {channel.value}')
print(f'ADC Voltage: {str( channel.voltage )}V')
print(f'Resistance: {resistance(channel.value)}')
print(f'Temperature?: {str(steinhart_temperature_C(resistance(channel.value)))}')
