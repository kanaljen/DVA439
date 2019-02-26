import json
import sys


def checkArgv(argv):
    if len(argv)!=2:
        print('wrong number of arguments')
        print('usage:', argv[0], '<jsonfile>')
        exit(0)
    dot = argv[1].find('.')
    if argv[1][dot:] != '.json':
        print('not a json file')
        print('usage:', argv[0], '<jsonfile>')
        exit(0)


def read_json(file):
    with open(file) as json_data:
        return json.load(json_data)


def main(argv):
    checkArgv(argv)
    data = read_json(argv[1])
    print(data)


if __name__ == "__main__": main(sys.argv)