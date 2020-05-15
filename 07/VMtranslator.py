import sys
from enum import Enum

class Comm(Enum):
    ARITHMETIC = "ARITHMETIC"
    PUSH = "PUSH"
    POP = "POP"
    LABEL = "LABEL"
    GOTO = "GOTO"
    IF = "IF"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    CALL = "CALL"
    ERR = "ERR"


class Parser:
    def __init__(self, filename):
        self._f = open(filename, "r")
        self._command = ""
        self._next = self._f.readLine()

    def hasMoreCommands(self):
        return self._next != None

    def advance(self):
        if self.hasMoreCommands():
            self._command = self._next
            self._next = self._f.readLine()
        else:
            print("err: the file is empty")

    def commandType(self):
        arithList = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        parse = self._command.split(' ')
        if parse[0] == "push":
            return Comm.PUSH
        elif parse[0] == "pop":
            return Comm.POP
        elif parse[0] in arithList:
            return Comm.ARITHMETIC
        else:
            return Comm.ERR

    def comm(self):
        return self._command.split(' ')[0]
    
    def arg1(self):
        return self._command.split(' ')[1]

    def arg2(self):
        allowList = [Comm.PUSH, Comm.POP, Comm.FUNCTION, Comm.CALL]
        if self.commandType() in allowList:
            return self._command.split(' ')[2]
        else:
            return ""

    def __del__(self):
        self._f.close()


class CodeWriter:
    def __init__(self, filename):
        self._f = open(filename, "w")
        self._count = 0

    def _next(self):
        self._count = self._count + 1
        return self._count - 1

    def _segToAddress(self, segment):


    def writeArithmetic(self, command):
        if command == "neg" or command == "not":
            self._f.write("@SP\nA=M\nA=A-1\n")
            if command == "neg":
                self._f.write("M=-M")
            else:
                self._f.write("M=!M")
        else:
            self._f.write("@SP\nM=M-1\nA=M\nD=M\nM=0\nA=A-1\n")
            if command == "add":
                self._f.write("M=D+M\n")
            elif command == "sub":
                self._f.write("M=D-M\n")
            elif command == "eq":
                self._f.write("D=D-M\n@IF.{0}\nD;JEQ\n@ELSE.{0}\n0;JMP\n(IF.{0})\nM=-1\n@IFEND.{0}\n(ELSE.{0})\nM=0\n(IFEND.{0})".format(self._next()))
            elif command == "gt":
                self._f.write("D=D-M\n@IF.{0}\nD;JGT\n@ELSE.{0}\n0;JMP\n(IF.{0})\nM=-1\n@IFEND.{0}\n(ELSE.{0})\nM=0\n(IFEND.{0})".format(self._next()))
            elif command == "lt":
                self._f.write("D=D-M\n@IF.{0}\nD;JLT\n@ELSE.{0}\n0;JMP\n(IF.{0})\nM=-1\n@IFEND.{0}\n(ELSE.{0})\nM=0\n(IFEND.{0})".format(self._next()))
            elif command == "and":
                self._f.write("M=D&M\n")
            elif command == "or":
                self._f.write("M=D|M\n")

    def writePushPop(self, command, segment, index):
        if command == Comm.POP:
            self._f.write("@SP\nM=M-1\n")
        if command == Comm.PUSH:
            if segment == "local":
                self._f.write("@LCL\nD=M\n@{0}\nA=D+A\n".format(index))
            elif segment == "argument":
                self._f.write("@ARG\nD=M\n@{0}\nA=D+A\n".format(index))
            elif segment == "this":
                self._f.write("@THIS\nD=M\n@{0}\nA=D+A\n".format(index))
            elif segment == "that":
                self._f.write("@THAT\nD=M\n@{0}\nA=D+A\n".format(index))
            elif segment == "pointer":
                self._f.write("@{0}\n".format(3 + index))
            elif segment == "temp":
                self._f.write("@{0}\n".format(5 + index))
            self._f.write("D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == Comm.POP:
            self._f.write("D=A\n@SP\n")

    def __del__(self):
        self._f.close()

def main(filename):
    parser = Parser(filename + ".vm")
    codeWriter = CodeWriter(filename + ".asm")
    while(parser.hasMoreCommands()):
        parser.advance()
        if parser.commandType() == Comm.ARITHMETIC:
            codeWriter.writeArithmetic(parser.comm())
        elif parser.commandType() == Comm.PUSH:
            codeWriter.writePushPop(Comm.PUSH, parser.arg1(), parser.arg2())
        elif parser.commandType() == Comm.POP:
            codeWriter.writePushPop(Comm.POP, parser.arg1(), parser.arg2())

if __name__ == "__main__":
    main(sys.argv[1])