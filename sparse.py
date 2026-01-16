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
            s += s
    return s


functionReplacements = {
    "&":" and ",
    "^":" or ",
    "!":" not "
}
argumentReplacements = {
    "T":"True",
    "F":"False",
    "t":"True",
    "f":"False"
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

    def table(self):
        curArgs = [False]*len(self.arguments)
        header = f"| {','.join(self.arguments)}\t| ({self.name}) {self.text}\t|"
        print('-'*len(header)+10*'-')
        print(header)
        print('-'*len(header)+10*'-')
        i = 0
        while True:
            for idx,c in enumerate(pad(str(bin(i))[2:], "0", len(self.arguments), left=True)):
                if c == "1":
                    curArgs[idx] = True
                elif c == "0":
                    curArgs[idx] = False
            print(f"| {','.join([str(e) for e in curArgs])}\t| {self.fn(*curArgs)}\t|")
            if curArgs == [True]*len(self.arguments):
                break
            i += 1
        print('-'*len(header)+10*'-')

def evaluate(fn):
        name, fn = fn.split("=")
        name = name.replace(" ", "")
        formattedInput = ""
        arguments = []
        for c in fn:
            if c in possibleArguments and c not in arguments:
                arguments += c  
        for c in fn:
            if c in functionReplacements:
                formattedInput += functionReplacements[c]
            else:
                formattedInput += c
        lambaFormat = f"{name}_user = lambda {','.join(arguments)}: {formattedInput}"
        exec(lambaFormat, locals())
        userFns[name+"_user"] = fn
        print(f"Executing {lambaFormat} ...")

while True:
    i = input(">>> ")
    print(i.split(" "))
    if "=" in i:
        t = Sentence(i.split("=")[0], i.split("=")[1])
        userFns[t.name+"_user"] = t
    elif i.split(" ")[0] == "table":
        t = Sentence("anon",i.split(" ")[1])
        print(t.table())
    else:
        fn = i.split("{")[0]
        args = i.split("{")[1]
        if args[-1] == "}":
            args = args[:-1]
        for i in argumentReplacements:
            args.replace(i,argumentReplacements[i])
        print(userFns[fn+"_user"].fn(*args.split(",")))