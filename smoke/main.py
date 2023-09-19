from time import sleep
from smoke.fan import Fan
from smoke.maintain import maintain
from smoke.thermistor import Probes


def main() -> None:
    # set up probes 1 & 2 w/ air on 1 & food on 2
    probes = Probes([1, 2])
    air = probes.get_probe(1)
    food = probes.get_probe(2)

    # set up the fan on GPIO pin 2
    with Fan(2) as fan:
        # get the desired target temp as an input
        target = float(
            input("Please enter a desired target temperature in Celsius:"))
        # begin maintaining the desired temp
        # FIXME: this won't need to track food temp later
        if air is not None and food is not None:
            print(f'Maintaining a target temp of {target}' +
                  'C, enter CTRL-C to quit')
            maintain(target, air, fan, food)
        else:
            print("There is no air probe plugged in on channel 1")


if __name__ == "__main__":
    main()
