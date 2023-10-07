import os
from os import path
import glob
import sys
import re

# Default start dir
here = os.path.dirname(__file__)

#Supported file extensions
supported_formats = ["psd", "tga"]

#Regex to filter out dis allowed files
ignored_files_regex = r"(\\work)|(\\[a-z]*_gitblock)"

def GetGameInfoPath(dir):
    return path.join(dir, "game", "tf")

def ProcessFiles():
    gameinfo = GetGameInfoPath(here)
    while not path.exists(gameinfo) and not path.exists(path.join(gameinfo, "gameinfo.txt")):
        print("Enter valid path where gameinfo.txt exists:")
        gameinfo = input()

    content = path.normpath(path.join(gameinfo, "..", "..", "content"))
    game = path.normpath(path.join(gameinfo, ".."))
    vtex = path.join(game, "bin", "vtex.exe")

    if not path.exists(content):
        print(f"Content path '{content}' does not exist? Aborting.")
        exit(1)

    to_compile: set[str] = set()
    for ext in supported_formats:
        to_compile.update(glob.glob("./**/*." + ext, root_dir=content, recursive=True))

    print(f">>> 🔍 Found {len(to_compile)} files to process")

    for file in to_compile:
        if len(re.findall(ignored_files_regex, file, flags=re.IGNORECASE)) == 0:
            ProcessFile(vtex, gameinfo, content, game, file)
        else:
            print(f">>> Skipped {file} due to ignore expression")
    
def ProcessFile(vtex: str, gameinfo: str, content: str, game: str, file: str):
    outdir = path.normpath(path.join(game, file, ".."))
    vtexcmd = f"{vtex} -game {gameinfo} -outdir {outdir} -nopause {path.normpath(path.join(content, file))}"

    print("> " + vtexcmd)
    result = os.system(vtexcmd)
    if os.name != "nt":
        result = os.waitstatus_to_exitcode(result)
    
    if result != 0:
        print(f">>> ❌ Failed when executing VTFCmd, Code: {result}")
    else:
        print(f">>> ✓ Success processing '{file}'!")

if len(sys.argv) > 1:
    here = sys.argv[1]
    if not path.exists(here):
        here = path.join(__path__, sys.argv[1])

if not path.exists(here):
    print(f"Given dir '{here}' does not exist")
    exit(1)

ProcessFiles()