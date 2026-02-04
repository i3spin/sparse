#!/usr/bin/env python
'''
This is a Symbolic logic PARSEr (SPARSE)
'''

import platform
import traceback
import argparse
import sys
import dbg

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

def split_not_in(s, val, startIgnore, endIgnore):
    if s in [None, ""]:
        return s
    ignore = False
    returnList = []
    curSlice = ""
    for i in s:
        if i == val and not ignore:
            returnList.append(curSlice)
            curSlice = ""
        else:
            curSlice += i
        if i == startIgnore:
            ignore = True
        elif i == endIgnore:
            ignore = False
    returnList.append(curSlice)
    return returnList

def arg_sub(function, args):

    if args[0] == "{":
        args = args[1:]
    if args[-1] == "}":
        args = args[:-1]
    args = split_not_in(args, ",", "{", "}")

    functionBody = userFns[function].text
    argNames = userFns[function].arguments
    d.dbg(f"functionBody = {functionBody}; argNames = {argNames}")
    subbedFunction = ""
    for char in functionBody:
        d.dbg(f"subbedFunction = {subbedFunction}")
        d.dbg(f"Working on {char}")
        if char in argNames:
            d.dbg(f"argumnet, appending ({args[argNames.index(char)]})")
            subbedFunction += args[argNames.index(char)]
        else:
            d.dbg(f"not argument")
            subbedFunction += char
        
    if subbedFunction[-1] == "}":
        subbedFunction = subbedFunction[:-1]
    d.dbg(f"returning {subbedFunction}", clr='yellow')
    return "("+subbedFunction+")"



functionReplacements = {
    "&":" and ",
    "^":" and ",
    "v":" or ",
    "!":" not "
}
functionOutputReplacements = {
    1:True,
    0:False,
    True:True,
    False:False
}
argumentReplacements = {
    "True":"True",
    "False":"False",
    "T":"True",
    "F":"False",
    "t":"True",
    "f":"False",
    "0":"0",
    "1":"1"
}

possibleArguments = "ABCDEGHIJKLMNOPQRSUVWXYZabcdeghijklmnopqrsuwxyz"

userFns = {}

class Sentence:
    global userFns
    def __init__(self, name, body):
        self.name = name
        self.ogText = body.lstrip()
        self.name = self.name.replace(" ", "")
        self.text = gen_func_helper(body)
        self.arguments = []
        for c in self.text:
            if c in possibleArguments and c not in self.arguments and c not in argumentReplacements:
                self.arguments.append(c)
        self.arguments = sorted(self.arguments)

        formattedInput = ""
        for c in self.text:
            if c in functionReplacements:
                formattedInput += functionReplacements[c]
            elif c in argumentReplacements:
                formattedInput += argumentReplacements[c]
            else:
                formattedInput += c

        self.lambdaFormat = f"f = lambda {','.join(self.arguments)}: {formattedInput}"
        if VERBOSE:
            print(f"Defining '{self.name}' as '{self.lambdaFormat}'.")
        t = {}
        exec(self.lambdaFormat, t)
        for i in t:
            self.fn = t[i] 
        userFns[self.name] = self

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
            truthDict[nStr] = self.run(curArgs)
            if curArgs == [True]*len(self.arguments):
                break
            i += 1
        return truthDict

    def table(self):
        truthDict = self.gen_table()
        sec1, sec2 = f" {','.join(self.arguments)} ", f" ({self.name}) {self.ogText} "
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
            out = out[:-1] 
            out = pad(out," ",sectionLens[0]+1)
            out += "| "
            out += f"{truthDict[i]}"
            out = pad(out, " ", sectionLens[0]+sectionLens[1]+2) + "|"
            print(out)
        print(separator)

    def run(self, args):
        for idx,a in enumerate(args):
            if a in argumentReplacements:
                args[idx] = argumentReplacements[a]
        d.dbg(f"Running {self.lambdaFormat} with {args}")
        result = self.fn(*args)
        if result in functionOutputReplacements:
            return functionOutputReplacements[result]
        else:
            error(f"The function {self.text} gave bad output '{result}'.")  
    
    def print_func(self):
        cols = [["Function Name"],["User Definition"],["Fully Substituted Definition"],["Lambda Function Definition"]]
        for i in range(len(cols)):
            cols[i].append("-"*len(cols[i][0]))
        cols[0].append(self.name)
        cols[1].append(self.ogText)
        cols[2].append(self.text)
        cols[3].append(self.lambdaFormat)
        longests = [0]*len(cols)
        for i in range(len(cols)):
            for e in cols[i]:
                if len(e) > longests[i]:
                    longests[i] = len(e)
        print() 
        for i in range(len(cols[0])):
            for idx in range(len(cols)):
                print(pad(cols[idx][i], " ", longests[idx]+1),end='\t')
            print()
        print()

    
    def __eq__(self,other):
        return (self.gen_table() == other.gen_table())

def list_funcs():
    out = []
    for func in userFns:
        out.append(f"{userFns[func].name}")
    if out == []:
        return
    longest = 0
    for func in out:
        if len(func) > longest:
            longest = len(func) 
    print()
    for idx,func in enumerate(out):
        out[idx] = pad(func, " ", longest)
        out[idx] += f" : {userFns[func].ogText}"
        print(out[idx])
    print()

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

def clear_screen():
    print("\033[2J\033[H", end="", flush=True)

def display_help():
    cols = [["COMMAND"],["DESCRIPTION"],["ARGUMENTS"]]
    for i in range(len(cols)):
        cols[i].append("-"*len(cols[i][0]))
    for c in commandHelps:
        cols[0].append(c)
        cols[1].append(commandHelps[c][0])
        cols[2].append(commandHelps[c][1])
    longests = [0,0,0]
    for i in range(len(cols)):
        for e in cols[i]:
            if len(e) > longests[i]:
                longests[i] = len(e)
    print() 
    for i in range(len(cols[0])):
        for idx in range(len(cols)):
            print(pad(cols[idx][i], " ", longests[idx]+1),end='\t')
        print()
    print()

def gen_func_helper(i):

    parsedString = i

    if "{" in i:           
        for fn in userFns:
            start = 0
            end = start + len(fn)
            while end < len(i):
                end = start + len(fn)
                d.dbg(f"fn = {fn} ; chunk = {parsedString[start:end]}")
                if parsedString[start:end] == fn:
                    if parsedString[end] == "{":
                        d.dbg("made it here")
                        # we have arguments
                        argsEnd = end+1
                        argString = "{"
                        depth = 1
                        while depth >= 1 and argsEnd < len(parsedString):
                            if parsedString[argsEnd] == "{":
                                depth += 1
                            elif parsedString[argsEnd] == "}":
                                depth -= 1
                            d.dbg(f"added {i[argsEnd]} to argString")
                            argString += parsedString[argsEnd]
                            argsEnd += 1
                        d.dbg(f"substituting with fn = {fn}, argString = {argString}")
                        substitutedFunction = arg_sub(fn, argString)
                        parsedString = parsedString[:start] + substitutedFunction + parsedString[argsEnd:]
                        d.dbg(f"parsedString = {parsedString}",clr='yellow')
                        d.dbg(f"substituedFunction = {substitutedFunction}")
                        return gen_func_helper(parsedString)
                    
                    elif parsedString[end] in functionReplacements:
                        # there are no arguments so just append the functions whole body
                        parsedString = parsedString[:start] + userFns[fn].text + parsedString[end:]
                        return gen_func_helper(parsedString)
                start += 1
    
    else:
        for fn in userFns:
            if fn in i:
                i = i.replace(fn, "("+userFns[fn].text+")")
                return gen_func_helper(i)
        return i                

commandHelps = {
    "help":["Display this help menu.","none"],
    "cls, clear":["Clears screen.","none"],
    "list":["Lists defined function names and bodies.","none"],
    "table":["Displays truth table for given function.","1 (function to table)"],
    "load":["Execute every line in a given file like it had been typed into SPARSE.","1 (file to load)"],
    "print":["Prints function body and fully substituted definition for function.","1 (function to print)"]
}

commands = {
    "help":lambda i : display_help(),
    "cls":lambda i : clear_screen(),
    "clear":lambda i : clear_screen(),
    "list":lambda i : list_funcs(),
    "table":lambda i : error("'table' takes a function to table.") if len(i.split(" ")) != 2 else print_table(i.split(" ")[1]),
    "load":lambda i : error("'load' takes a file to load") if len(i.split(" ")) != 2 else load(i.split(" ")[1]),
    "print":lambda i : error("'print' takes a function to print") if len(i.split(" ")) != 2 else userFns[i.split(" ")[1]].print_func(),
    "==":lambda i : error("you must have two or more functions for comparison") if len(i.split("==")) < 2 else equivalent([ f.replace(" ","") for f in i.split("==")]),
    "=":lambda i : error("you must have a name and a body for a function definition") if (len([a for a in i.split("=") if a.replace(" ", "") != ""]) != 2) else assign(i.split("=")[0].replace(" ",""),i.split("=")[1]),
    "{":lambda i : print(Sentence("anon",i).run([]))
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
        error(f"There was an exception '{e}' during execution.")
        if ARGS.devmode:
            traceback.print_exc()


if platform.system() == "Linux" or platform.system() == "Darwin":
    import readline

VERSION = 2.0

VERBOSE = False
DEV_MODE = False
parser = argparse.ArgumentParser(description="Symbolic logic PARSEr (SPARSE) version 1")
parser.add_argument("--devmode", action="store_true", help="Turn on developer mode.")
parser.add_argument("--verbose", action="store_true", help="Be more verbose about what SPARSE is doing.")
parser.add_argument("-f", "--file", type=str, help="Run SPARSE on a file then quit.")
ARGS = parser.parse_args()

if __name__ == "__main__":
    VERBOSE, DEV_MODE = ARGS.verbose, ARGS.devmode
    if DEV_MODE:
        VERBOSE = True
    if not VERBOSE:
        d = dbg.debug(args=" : -10 sps=t suppressWarnings=t suppressInfo=t")
    else:
        d = dbg.debug(args=sys.argv)

    if ARGS.file != None:
        load(ARGS.file)
    else:
        print(f"Welcome to SPARSE (Symbolic logic PARSEr) version {VERSION}. Type 'help' for a list of commands and uses.")
        print("Read the README.md for explanation of syntax and usage. Enjoy!")
        print("AUTHOR: James Burkett (Xtreme Software Developers) ; (xtremesoftwaredev@gmail.com)")
        while True:
            i = input("sparse> ")
            parse(i)
else:
    warn("Not running as main")
