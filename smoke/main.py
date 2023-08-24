from time import sleep
from smoke.thermosistor import setup_probes


def main() -> None:
    probes = setup_probes([1])

    while True:
        print(f'Temperatures: {probes}\n')
        sleep(1)


if __name__ == "__main__":
    main()
