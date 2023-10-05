import os
from os import path
import glob
import sys

here = os.path.dirname(__file__)

supported_formats = ["psd", "tga"]

def GetGameInfoPath(dir):
    return path.join(dir, "game", "tf", "gameinfo.txt")

def ProcessFiles():
    gameinfo = GetGameInfoPath(here)
    while not path.exists(gameinfo):
        print("Enter path of gameinfo:")
        gameinfo = input()

    content = path.normpath(path.join(gameinfo, "..", "..", "..", "content"))
    game = path.normpath(path.join(gameinfo, "..", ".."))
    vtex = path.join(game, "bin", "vtex.exe")

    if not path.exists(content):
        print(f"Content path '{content}' does not exist? Aborting.")
        exit(1)

    to_compile = []
    for ext in supported_formats:
        to_compile.extend(glob.glob("./**/*." + ext, root_dir=content, recursive=True))

    print(f"Found {len(to_compile)} files")

    
    
def ProcessFile(vtex: str, gameinfo: str, content: str, game: str, file: str):
    vtexcmd = f"{vtex} -game {gameinfo} -outdir {content} -nopause {file}"

    print("> " + vtexcmd)
    result = os.system(vtexcmd)
    if os.name != "nt":
        result = os.waitstatus_to_exitcode(result)
    
    if result != 0:
        raise Exception(f"Failed when executing VTFCmd, Code: {result}")
    else:
        print(f"Success!")

if len(sys.argv) > 1:
    here = sys.argv[1]
    if not path.exists(here):
        here = path.join(__path__, sys.argv[1])

if not path.exists(here):
    print(f"Given dir '{here}' does not exist")
    exit(1)

ProcessFiles()