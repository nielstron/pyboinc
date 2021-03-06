"""
Convert .h definitions (especially constants and enums) to python code
"""
from fileinput import FileInput
from re import finditer
from pathlib import Path
from sys import stdin

if __name__ == '__main__':
    constants = set()
    enums = dict()
    enum = None
    with FileInput() as file:
        for line in file:
            for res in finditer(r"enum\s*([A-Z1-9_]+)\s*\{", line):
                enum = (res[1], set())
            for res in finditer(r"#define\s+([A-Z1-9_]+)\s+(\d+)", line):
                constants.add((res[1], res[2]))
            for res in finditer(r"([A-Z1-9_]+)\s*=\s*(\d+)\s*,", line):
                enum[1].add((res[1], res[2]))
            for res in finditer(r"\};", line):
                if enum:
                    enums[enum[0]] = enum[1]
                    enum = None

    print("# generated by h_to_py.py")
    print("from enum import Enum")
    print()
    print()
    print("class Constants:")
    for c_name, c_value in sorted(constants):
        print("    {} = {}".format(c_name, c_value))
    for enum, enum_constants in enums.items():
        print()
        print()
        print("class {}(Enum):".format(enum))
        for c_name, c_value in enum_constants:
            print("    {} = {}".format(c_name, c_value))
