#!/usr/bin/env python
'''
This is a Symbolic logic PARSEr (SPARSE)
'''

import readline
import traceback
import argparse


colors = {'blue': '\033[31;1;34m',
          'yellow': '\033[31;1;33m',
          'green': '\033[31;1;32m',
          'red': '\033[31;1m',
          'purple':'\033[1;35m',
          'cyan':'\033[1;36m',
          'bold': '\033[0;1m',
          'none': '\033[0m'}

def error(txt):
    print(f"{colors['red']}ERROR: {txt}{colors['none']}")

def warn(txt):
    print(f"{colors['yellow']}WARNING: {txt}{colors['none']}")

def pad(s, val, l, left=False):
    while len(s) < l:
        if left:
            s = val + s
        else:
            s += val
    return s

def by_two(ls):
    rtnLs = []
    i = 0
    while i+1 <= len(ls)-1:
       rtnLs.append([ls[i], ls[i+1]]) 
       i += 1
    return rtnLs

functionReplacements = {
    "&":" and ",
    "^":" and ",
    "|":" or ",
    "!":" not "
}
argumentReplacements = {
    "True":"True",
    "False":"False",
    "T":"True",
    "F":"False",
    "t":"True",
    "f":"False",
    "0":0,
    "1":1
}

possibleArguments = "10ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

userFns = {}

class Sentence:
    global userFns
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.name = self.name.replace(" ", "")
        formattedInput = ""
        self.arguments = []
        replacingFunctions = True
        while replacingFunctions:
            replacingFunctions = False
            for c in userFns:
                if userFns[c].name in self.text:
                    self.text = self.text.replace(userFns[c].name, "("+userFns[c].text+")")
                    replacingFunctions = True
        for c in self.text:
            if c in possibleArguments and c not in self.arguments:
                self.arguments.append(c) 
        for c in self.text:
            if c in functionReplacements:
                formattedInput += functionReplacements[c]
            else:
                formattedInput += c
        lambdaFormat = f"f = lambda {','.join(self.arguments)}: {formattedInput}"
        t = {}
        exec(lambdaFormat, t)
        for i in t:
            self.fn = t[i] 
        try:
            self.fn(*(("0,"*len(self.arguments))[:-1]).split(","))
        except:
            error(f"failed to define '{self.name}' as '{lambdaFormat}'. Most likely there is a syntax error in your function definition.")
            return
        userFns[self.name] = self
        if ARGS.verbose:
            print(f"Defined '{self.name}' as '{lambdaFormat}'.")

    def gen_table(self):
        truthDict = {}
        curArgs = [False]*len(self.arguments)
        i = 0
        while True:
            nStr = pad(str(bin(i))[2:], "0", len(self.arguments), left=True)
            for idx,c in enumerate(nStr):
                if c == "1":
                    curArgs[idx] = True
                elif c == "0":
                    curArgs[idx] = False
            truthDict[nStr] = self.fn(*curArgs)
            if curArgs == [True]*len(self.arguments):
                break
            i += 1
        return truthDict

    def table(self):
        truthDict = self.gen_table()
        sec1, sec2 = f" {','.join(self.arguments)} ", f" ({self.name}) {self.text} "
        header = sec1 + "|" + sec2
        sectionLens = [len(sec1), len(sec2)]
        header = "|" + header + "|"
        separator = '+'+'-'*(sectionLens[0])+'+'+'-'*(sectionLens[1])+'+'
        print(separator)
        print(header)
        print(separator)
        r = {"0":"F","1":"T"}
        for i in truthDict:
            out = "| "
            for c in i:
                out += r[c]+","
            # print(f"'{out}'")
            out = out[:-1] 
            # print(f"'{out}'")
            out = pad(out," ",sectionLens[0]+1)
            # print(f"'{out}'")
            out += "| "
            # print(f"'{out}'")
            out += f"{truthDict[i]}"
            # print(f"'{out}'")
            out = pad(out, " ", sectionLens[0]+sectionLens[1]+2) + "|"
            # print(f"'{out}'")
            print(out)
        print(separator)
    
    def __eq__(self,other):
        return (self.gen_table() == other.gen_table())

def list_funcs():
    out = []
    for func in userFns:
        out.append(f"{userFns[func].name}")
    longest = 0
    for func in out:
        if len(func) > longest:
            longest = len(func) 
    for idx,func in enumerate(out):
        out[idx] = pad(func, " ", longest)
        out[idx] += f" : {userFns[func].text}"
        print(out[idx])

def print_table(fToTable):
    if fToTable in userFns:
        t = userFns[fToTable]
    else:
        t = Sentence("anon",fToTable)
    t.table()

def load(file):
    print(f"Loading file '{file}'...")
    try:
        with open(file, "r") as f:
            wholeFile = f.readlines()
        for ln in wholeFile:
            parse(ln)
        print("Done!")
    except Exception as e:
        error(f"failed to load file with exception {e}")

def print_func(fToPrint):
    if fToPrint not in userFns:
        error(f"couldn't find a definition for '{fToPrint}'")
        return
    print(f"{userFns[fToPrint].name} : {userFns[fToPrint].text}")

def assign(name,text):
    t = Sentence(name, text)
    userFns[t.name] = t

def equivalent(fns):
    for idx,f in enumerate(fns):
        fns[idx] = Sentence("anon",f)
    result = True
    for c in by_two(fns):
        if c[0] != c[1]:
            result = False 
            break
    print(result)

def evaluate(f,args):
    filteredArgs = []
    for a in args:
        if a in argumentReplacements:
            filteredArgs.append(argumentReplacements[a])
        if a in possibleArguments:
            filteredArgs.append(a)
    argDiff = len(userFns[f].arguments)-len(filteredArgs)
    if argDiff != 0:
        error(f"You're missing {argDiff} arguments for function {f}.")
    print(userFns[f].fn(*filteredArgs))

def clear_screen():
    print("\033[2J\033[H", end="", flush=True)

commands = {
    "cls":lambda i : clear_screen(),
    "clear":lambda i : clear_screen(),
    "list":lambda i : list_funcs(),
    "table":lambda i : error("'table' takes a function to table.") if len(i.split(" ")) != 2 else print_table(i.split(" ")[1]),
    "load":lambda i : error("'load' takes a file to load") if len(i.split(" ")) != 2 else load(i.split(" ")[1]),
    "print":lambda i : error("'print' takes a function to print") if len(i.split(" ")) != 2 else print_func(i.split(" ")[1]),
    "==":lambda i : error("you must have two or more functions for comparison") if len(i.split("==")) < 2 else equivalent([ f.replace(" ","") for f in i.split("==")]),
    "=":lambda i : error("you must have a name and a body for a function definition") if (len([a for a in i.split("=") if a.replace(" ", "") != ""]) != 2) else assign(i.split("=")[0].replace(" ",""),i.split("=")[1]),
    "{":lambda i : evaluate(i.split("{")[0],i.split("{")[1]),
}

def parse(i):
    i = i.strip()
    if i == "":
        return
    try:
        for c in commands:
            if c in i:
                commands[c](i)
                return
        error(f"SPARSE couldn't figure out what you wanted")

    except Exception as e:
        print(f"There was an exception '{e}' during execution.")
        if ARGS.devmode:
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Symbolic logic PARSEr (SPARSE) version 1")
    parser.add_argument("--devmode", action="store_true", help="Turn on developer mode.")
    parser.add_argument("--verbose", action="store_true", help="Be more verbose about what SPARSE is doing.")
    ARGS = parser.parse_args()
    while True:
        i = input("sparse> ")
        parse(i)
else:
    warn("Not running as main")