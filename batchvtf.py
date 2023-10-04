# Batch VTF Compiler (via vtfcmd)
# Reads options from txt files

import os
import re
from typing import Callable

here = os.path.dirname(__file__)
_in = os.path.join(here, "in")
_out = os.path.join(here, "out")

supported_formats = ["psd", "png", "tga", "jpg"]

#Default arguments
defaults = {
    #"maxwidth": "rwidth 512"
}

#Arg Mapping
# Add new ones below 🔽🔽
# {} is where the data is put (e.g. -rclampwidth 512)
arg_mapping: dict[str, str] = {
    "maxwidth": "rwidth {}",
    "maxheight": "rheight {}",
    "srgb": "srgb",
    "dxt5": "format DXT5",
    "nomip": "nomipmaps",
    "normal": "normal",
    "bumpscale": "bumpscale {}"
}

#Flags
flags = [
    "POINTSAMPLE",
    "TRILINEAR",
    "CLAMPS",
    "CLAMPT",
    "ANISOTROPIC",
    "HINT_DXT5",
    "NORMAL",
    "NOMIP",
    "NOLOD",
    "MINMIP",
    "PROCEDURAL",
    "RENDERTARGET",
    "DEPTHRENDERTARGET",
    "NODEBUGOVERRIDE",
    "SINGLECOPY",
    "NODEPTHBUFFER",
    "CLAMPU",
    "VERTEXTEXTURE",
    "SSBUMP",
    "BORDER"
]

#Special Arg Mappings
func_arg_mapping: dict[str, Callable[[str, str], list[str]]] = {
    #"?": lambda : ["?"]
}

def SupportedFile(filepath: str) -> bool:
    for format in supported_formats:
        if filepath.endswith(format):
            return True
        
    return False

def ProcessFiles():
    files_to_process: dict[str, str] = {}

    # Verify in dir exists or ask for alt dir
    global _in
    if not os.path.exists(_in):
        print("Enter input path:")
        new_in = input()
        if not os.path.exists(new_in):
            new_in = os.path.join(here, new_in)
            if not os.path.exists(new_in):
                print("ERROR: provided input path cannot be found")
                exit(1)
        
        _in = new_in

    print(f"Looking for files in '{_in}'")
    for file in os.listdir(_in):
        file = file.lower()
        if SupportedFile(file):
            split = os.path.splitext(os.path.basename(file))
            name = split[0]
            ext = split[1]
            #If file name already seen, keep one with higher priority ext
            if name in files_to_process:
                current_i = supported_formats.index(os.path.splitext(os.path.basename(files_to_process[name])))
                new_i = supported_formats.index(ext)
                if(new_i < current_i):
                    print(f"Found better file: {file}")
                    files_to_process[name] = file
            else:
                print(f"Found: {file}")
                files_to_process[name] = file

    for file in files_to_process.values():
        options = GetCustomArguments(os.path.join(_in, file))
        ProcessFile(file, options)

#Product list of arguments for cmd
def GetCustomArguments(filepath: str) -> list[str]:
    options = defaults.copy()
    options_filename = os.path.splitext(filepath)[0] + ".txt"
    if os.path.exists(options_filename):
        f = open(options_filename, "r")
        flags: list[str] = [];
        for line in f.readlines():
            line = line.replace("\n", "")
            if(len(line) != 0):
                ConvertArg(line, options, flags)
        f.close()

        #Create flag argument
        if(len(flags) != 0):
            flag_option = "-flag"
            for flag in flags:
                flag_option += " " + flag
            options["flag"] = flag_option

    return options.values()

#Read line and convert to argument for vtfcmd
def ConvertArg(arg_line: str, options: dict[str, str], flags: list[str]) -> bool:
    arg_split = arg_line.split(" ")
    flag: str = arg_split[0]

    if len(arg_split) >= 2:
        flag_arg = arg_split[1]
    else:
        flag_arg = ""

    if(flag in arg_mapping):
        options[flag] = "-" + arg_mapping[flag].format(flag_arg)
    elif(flag in func_arg_mapping):
        options[flag] = func_arg_mapping[flag](flag, flag_arg)
    elif(flag.upper() in flags):
        flags.insert(flag.upper())
    else:
        print(f"!! Unrecognised option '{flag}'")
        return False
    
    return True

#Execute vtf cmd for file and use provided args
def ProcessFile(filepath: str, args: list[str]):
    filename = os.path.basename(filepath)
    vtfcmdcmd = f"{os.path.join(here, 'VTFCmd.exe')} -file \"{os.path.join(_in, filepath)}\" -output \"{_out}\""
    #Add other arguments
    for arg in args:
        vtfcmdcmd += " " + arg

    # Add resize arg if required
    if(len(re.findall("(rwidth)|(rheight)", vtfcmdcmd)) != 0):
        vtfcmdcmd += " -resize"

    if not os.path.exists(_out):
        os.mkdir(_out)

    print("> " + vtfcmdcmd)
    result = os.system(vtfcmdcmd)
    if os.name != "nt":
        result = os.waitstatus_to_exitcode(result)
    
    if result != 0:
        raise Exception(f"Failed when executing VTFCmd, Code: {result}")
    else:
        print(f"Success!")


ProcessFiles()
print("== All Done ==")