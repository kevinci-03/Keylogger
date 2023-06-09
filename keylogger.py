import os;
from pynput.keyboard import Listener;

def main():
    with Listener(on_press=keyPress) as listener:
        listener.join();

def keyPress(key):
    print(str(key));

if __name__ == "__main__":
    main()