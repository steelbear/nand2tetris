import sys
import re

vc = 16

symbolTable = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576
}

compList = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000",
    "M": "110000",
    "!D": "001101",
    "!A": "110001",
    "!M": "110001",
    "-D": "001111",
    "-A": "110011",
    "-M": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "M+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "M-1": "110010",
    "D+A": "000010",
    "D+M": "000010",
    "D-A": "010011",
    "D-M": "010011",
    "A-D": "000111",
    "M-D": "000111",
    "D&A": "000000",
    "D&M": "000000",
    "D|A": "010101",
    "D|M": "010101",
}

jmpList = {
    "NULL": "000",
    "GT": "001",
    "EQ": "010",
    "GE": "011",
    "LT": "100",
    "NE": "101",
    "LE": "110",
    "MP": "111",
}

ccode = re.compile(r'(?P<dest>[AMD]{1,3})=(?P<cmp>[AMD]?[!\+\-\&\|]?[AMD10])')
jcode = re.compile(r'(?P<compare>[AMD0]);J(?P<jmp>GT|EQ|GE|LT|NE|LE|MP)')

def test_table():
    for symbol in symbolTable.keys():
        print(symbol + ":" + str(symbolTable[symbol]))

def isCcode(line):
    return ccode.match(line) != None or jcode.match(line) != None

def isLabel(line):
    return len(line) > 1 and line[0] == '(' and line[-1] == ')'

def decodeComp(dest, comp):
    code = "111"
    if "M" in comp:
        code += "1"
    else:
        code += "0"
    code += compList[comp]
    for d in "ADM":
        if d in dest:
            code += "1"
        else:
            code += "0"
    code += jmpList["NULL"]
    return code

def decodeJump(dest, jmp):
    code = "111"
    if "M" in dest:
        code += "1"
    else:
        code += "0"
    code += compList[dest]
    code += "000"
    code += jmpList[jmp]
    return code

def decodeA(line):
    global vc
    symbol = line[1:]
    if symbol in symbolTable.keys():
        return "{0:>016b}".format(int(symbolTable[symbol]))
    elif symbol.isdigit():
        return "{0:>016b}".format(int(symbol))
    else:
        symbolTable[symbol] = vc
        vc = vc + 1
        return "{0:>016b}".format(int(symbolTable[symbol]))

def decodeC(line):
    c = ccode.findall(line)
    j = jcode.findall(line)
    if c != []:
        return decodeComp(*c[0])
    elif j != []:
        return decodeJump(*j[0])
    else:
        print("err : cannot read C-code(" + line + ")")
        return ""

def readSymbol():
    with open(sys.argv[1], 'r') as f:
        pc = 0
        for raw in f:
            line = raw.strip().upper()
            if line == "" or line[0:2] == "//":
                continue
            elif isLabel(line):
                symbolTable[line[1:-1]] = pc
            else:
                pc = pc + 1

def decode():
    with open(sys.argv[1], 'r') as f:
        with open(sys.argv[1][:-3] + "hack", "w") as g:
            for raw in f:
                line = raw.strip().upper()
                if line == "" or line[0:2] == "//" or isLabel(line):
                    continue
                elif line[0] == '@':
                    g.write(decodeA(line) + "\n")
                elif isCcode(line):
                    g.write(decodeC(line) + "\n")
                else:
                    print(line)

readSymbol()
decode()