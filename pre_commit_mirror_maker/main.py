import argparse
import sys


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser()
    # args =
    parser.parse_args(argv)

    return 0


if __name__ == '__main__':
    exit(main())
