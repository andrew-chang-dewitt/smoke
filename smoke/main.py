from time import sleep
from smoke.thermistor import Probes


def main() -> None:
    probes = Probes([1])

    while True:
        print(f'Temperatures: {probes}\n')
        sleep(1)


if __name__ == "__main__":
    main()
