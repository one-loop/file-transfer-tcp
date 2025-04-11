import socket
import os
import json
import tkinter as tk
from tkinter import filedialog

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000

# Function to check if the file exists
def file_exists(filename):
    return os.path.isfile(filename)

def get_peers():
    with socket.socket() as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        s.send("GET_PEERS".encode())
        data = s.recv(4096).decode()
        return json.loads(data)

def chunk_file(filename, size=1024*512):
    chunks = []
    # read the file in raw binary chunks and write each chunk to a separate file
    with open(filename, "rb") as f:
        part_num = 0
        # each chunk is 512 KB (1024 * 512), read the file in 512 KB chunks
        while chunk := f.read(size):
            # create a new file for each chunk with a part number at the end
            # e.g. image.png.part0, image.png.part1, etc.
            name = f"{os.path.basename(filename)}.part{part_num}"  # Use basename of the file for chunk name
            with open(name, "wb") as c:
                c.write(chunk)
            
            # append the chunk name to the list, this will be used to register 
            # the chunk with the tracker and to upload the chunk to the peer
            chunks.append(name)
            part_num += 1
    
    # return the list of chunk names
    print(f"[ALICE] Created {len(chunks)} chunks for {filename}")
    return chunks

def upload_chunk(chunk_name, peer_host, peer_port):
    with socket.socket() as s:
        s.connect((peer_host, peer_port))
        s.send(f"UPLOAD|{chunk_name}".encode())
        ack = s.recv(1024).decode()
        if ack != "READY":
            print(f"[ALICE] Unexpected ack: {ack}")
            return
        with open(chunk_name, "rb") as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                s.sendall(bytes_read)

def register_chunk(chunk_name, filename, peer_port):
    with socket.socket() as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        message = f"REGISTER|{filename}|{chunk_name}|{peer_port}"
        s.send(message.encode())
        s.recv(1024)
        print(f"[ALICE] Registered {chunk_name} with tracker.")

def select_file():
    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter window
    # Open a file dialog to select the file to upload
    filename = filedialog.askopenfilename(title="Select a file to upload")
    return filename

def main():
    # Ask the user to select a file to upload
    filename = select_file()
    if not filename:
        print("[ALICE] No file selected. Exiting...")
        return

    if not file_exists(filename):
        print(f"[ALICE] The selected file does not exist: {filename}")
        return

    chunks = chunk_file(filename)
    peers = get_peers()  
    if not peers:
        print("[ALICE] No peers registered. Exiting...")
        return

    for i, chunk in enumerate(chunks):
        peer_host, peer_port = peers[i % len(peers)]
        upload_chunk(chunk, peer_host, peer_port)
        register_chunk(chunk, os.path.basename(filename), peer_port)  # Register using only the base filename
        os.remove(chunk)

    print("[ALICE] Upload and registration complete.")

if __name__ == "__main__":
    main()