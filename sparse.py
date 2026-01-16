#!/usr/bin/env python
'''
This is a Symbolic logic PARSEr (SPARSE)
'''

import readline

def pad(s, val, l, left=False):
    while len(s) < l:
        if left:
            s = val + s
        else:
            s += val
    return s


functionReplacements = {
    "&":" and ",
    "^":" and ",
    "|":" or ",
    "!":" not "
}
argumentReplacements = {
    "T":"True",
    "F":"False",
    "t":"True",
    "f":"False",
    "0":0,
    "1":1
}

possibleArguments = "abcdefghijklmnopqrstuvwxyz"

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
                    print(userFns[c].name,userFns[c].text)
                    self.text = self.text.replace(userFns[c].name, userFns[c].text)
                    replacingFunctions = True
        for c in self.text:
            if c in possibleArguments and c not in self.arguments:
                self.arguments.append(c) 
        for c in self.text:
            if c in functionReplacements:
                formattedInput += functionReplacements[c]
            else:
                formattedInput += c
        lambaFormat = f"{self.name}_user = lambda {','.join(self.arguments)}: {formattedInput}"
        t = {}
        exec(lambaFormat, t)
        for i in t:
            self.fn = t[i] 
        print(self.fn)
        userFns[self.name+"_user"] = self
        print(f"Executing {lambaFormat} ...")

    def gen_table(self):
        self.truthDict = {}
        curArgs = [False]*len(self.arguments)
        i = 0
        while True:
            nStr = pad(str(bin(i))[2:], "0", len(self.arguments), left=True)
            for idx,c in enumerate(nStr):
                if c == "1":
                    curArgs[idx] = True
                elif c == "0":
                    curArgs[idx] = False
            self.truthDict[nStr] = self.fn(*curArgs) 
            if curArgs == [True]*len(self.arguments):
                break
            i += 1

    def table(self):
        self.gen_table()
        curArgs = [False]*len(self.arguments)
        header = f" {','.join(self.arguments)} | ({self.name}) {self.text} "
        sectionLens = [len(header.split("|")[0])+1,len(header.split("|")[1])+1]
        header = "|" + header + "|"
        print(sectionLens)
        separator = '-'*len(header)+header.count("\t")*8*"-"
        print(separator)
        print(header)
        print(separator)
        r = {"0":"F","1":"T"}
        for i in self.truthDict:
            out = "| "
            for c in i:
                out += r[c]+","
            # print(f"'{out}'")
            out = out[:-1] 
            # print(f"'{out}'")
            out = pad(out," ",sectionLens[0])
            # print(f"'{out}'")
            out += "| "
            # print(f"'{out}'")
            out += f"{self.truthDict[i]}"
            # print(f"'{out}'")
            out = pad(out, " ", sectionLens[0]+sectionLens[1]) + "|"
            # print(f"'{out}'")
            print(out)
        print(separator)

while True:
    try:
        i = input(">>> ")
        print(i.split(" "))
        if i == "us":
            print(userFns)
        elif "=" in i:
            t = Sentence(i.split("=")[0], i.split("=")[1])
            userFns[t.name+"_user"] = t
        elif i.split(" ")[0] == "table":
            t = Sentence("anon",i.split(" ")[1])
            t.table()
        else:
            fn = i.split("{")[0]
            args = i.split("{")[1]
            args = args.split(",")
            if args[-1] == "}":
                args = args[:-1]
            for i in argumentReplacements:
                for b in range(len(args)):
                    if args[b] == i:
                        args[b] = argumentReplacements[i]
            print(userFns[fn+"_user"].fn(*args))
    except Exception as e:
        print(f"There was an exception '{e}' during execution.")