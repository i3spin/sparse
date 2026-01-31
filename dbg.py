'''
Simple debug class.
'''

yes = ['y', 'Y', 'yes', 'True', 'true', 't', 'T']
no = ['n', 'N', 'no', 'False', 'false', 'f' 'F']


class debug:

    def __init__(self, args="", separator=":", dfltLvl=0, dfltFunctions=["all"], dfltFunctionsToStop=[], defaultFlags={}, width1=10, width2=25, suppressWarnings=False, suppressInfo=False):
        import sys
        import traceback
        from datetime import datetime

        self.system = sys
        self.tb = traceback
        self.dt = datetime
        self.suppressWarnings = suppressWarnings
        self.suppressInfo = suppressInfo
        self.extraArgs = []

        self.colors =    {'blue': '\033[31;1;34m',
                    'yellow': '\033[31;1;33m',
                    'green': '\033[31;1;32m',
                    'red': '\033[31;1m',
                    'purple':'\033[1;35m',
                    'cyan':'\033[1;36m',
                    'bold': '\033[0;1m',
                    'none': '\033[0m'}

        # these have default values that can be overidden by flags
        self.functions = []
        self.functionsToStop = []
        self.width1 = width1
        self.width2 = width2
        self.debug = None

        # all true or false flags that can be set with cli args
        self.flags = {'dsplv': False, 'sps': False, 'tms': False, 'tb':False, 'suppressColors':False, 'suppressWarnings':suppressWarnings, \
                      'suppressInfo':suppressInfo, 'file':None, 'appendToTop':False}
        for curFlag in defaultFlags:
            self.flags[curFlag] = defaultFlags[curFlag]
        self.valueFlags = ['file']

        if type(args) == str:
            args = args.split(" ")
        idx = 0
        sepFound = False
        for i in args:
            idx += 1
            if i == separator:
                sepFound = True
                break

        if not sepFound:
            self.warn("py-dbg couldn't locate the separator in the argument list; using default values for all args (this could break stuff, use the separator!)")
        else:
            strippedArgs = args[idx:]
            self.extraArgs = args[:idx-1]
            try:
                for idx,i in enumerate(strippedArgs):

                    # check if it's an int, if so assume its debug level
                    try:
                        self.debug = int(i)
                        continue
                    except:
                        pass

                    # ensure that the argument isn't a float
                    try:
                        float(i)
                        self.warn(f"Argument number {idx} was a float, there shouldn't be any floats.")
                    except:
                        pass

                    # check to see if its a flag value
                    # the initial values are defaults, set them only if the flag is present
                    # we continue here because if the function returned true the thing was a flag so we don't need to keep going
                    if self.flag(i):
                        continue

                    # if it's none of the above, it's a function name
                    if i[0] == "=":
                        self.functionsToStop.append(i[1:])
                        self.functions.append(i[1:])
                    else:
                        self.functions.append(i)

            except:
                pass

        if len(self.functionsToStop) == 0:
            self.functionsToStop = dfltFunctionsToStop
            self.warn(f"You didn't specify any functions to stop on; using default:  {self.functionsToStop}")
        if len(self.functions) == 0:
            self.functions = dfltFunctions
            self.warn(f"You didn't specify any functions to debug; using default:    {self.functions}")
        if self.debug == None:
            self.debug = dfltLvl
            self.warn(f"You didn't specify any debug level, using default:           {self.debug}")

        self.info(f"The flag options are: {self.flags}.\n")


    # dinky little debug function
    def dbg(self, msg='Mark!', lvl=0, clr='bold', md='DEBUG', width1=10, width2=27, padVal=" ", end="\n", tb=False, ps=False, rtn=False):
        if lvl > self.debug and not rtn:
            return ""
        # get line and function name from sys alias (system)
        fn = self.system._getframe(1).f_code.co_name
        ln = str(self.color(self.system._getframe().f_back.f_lineno, 'green'))
        try:
            if  lvl < 0 or fn in self.functions or "all" in self.functions or \
                (fn == "<module>" and ("_module_" in self.functions)):
                ll = "LINE "+ln+";"
                if self.flags['dsplv']:
                    ll += f" LV [{self.color(lvl)}]; "
                while len(ll)-17 < width1:
                    ll += padVal
                l = f" FUNCTION <{self.color(fn, 'green')}>: "
                if self.flags['tms']:
                    ll += f" {self.color(self.dt.now().strftime('%Y-%m-%d %H:%M:%S'), 'yellow')}; "
                while len(l) - 20 < width2:
                    l += padVal

                out = f"{ll}{l}{self.color(msg, clr)}{end}"
                # only print if the debug level of the statement is less than the debug level the program is being run at
                if lvl <= self.debug:
                    if tb or self.flags['tb']:
                        # this chops off the format_stack call itself.
                        for i in self.tb.format_stack()[:-1]:
                            print(i)
                    if  fn in self.functionsToStop or "all" in self.functionsToStop or (ps and not self.flags['sps']) or \
                        (fn == "<module>" and ("_module_" in self.functionsToStop)):

                        if end == "\n":
                            end = ""
                        print(out,end='')
                        input()
                    else:
                        print(out,end='')
                    
                    if self.flags['file'] != None:
                        self.file_write(out, self.flags['file'], self.flags['appendToTop'])

                return out

        except Exception as e:
            self.warn(f"Debug function failed with '{e}' of type {type(e)}")

    def file_write(self, text, file, appendToTop):
        try:
            if appendToTop:
                with open(file, "r") as f:
                    fileText = f.read()
                fileText = text + fileText
                with open(file, "w") as f:
                    f.write(fileText) 
            else:
                with open(file, "a") as f:
                    f.write(text)
        except Exception as e:
            self.warn(f"Encountered exception attempting to write to file: {e}.")

    # return text with self.color delimiters
    def color(self, txt, color='bold'):
        if self.flags['suppressColors']:
            return txt
        else:
            return (f"{self.colors[color]}{txt}{self.colors['none']}")

    def flag(self, arg):
        for flagName in self.flags:
            try:
                sarg = arg.split("=")
                argFlagName = sarg[0]
                argFlagVal = sarg[1]

                if argFlagName == flagName:
                    if argFlagName in self.valueFlags:
                        self.flags[flagName] = argFlagVal
                    if argFlagVal in yes:
                        self.flags[flagName] = True
                        return True
                    if argFlagVal in no:
                        self.flags[flagName] = False
                        return True
                    else:
                        self.warn(f"Set value {argFlagVal} for flag {flagName} not valid.")
                        return True
            except:
                pass
        return False

    def warn(self, msg):
        out = f"{self.color('PY-DBG WARNING: ', 'red')} {self.color(msg, 'yellow')}"
        if not self.flags['suppressWarnings']:
            print(out)
        return out

    def info(self, msg):
        out = f"{self.color('PY-DBG INFO: ', 'purple')} {msg}"
        if not self.flags['suppressInfo']:
            print(out)
        return out
