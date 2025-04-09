# alice.py
import socket
import os

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000
# IMAGE_NAME = "image.png"
IMAGE_NAME = "img2.jpg"

PEERS = [("localhost", 7001), ("localhost", 7002)]  # Add more peers if needed

def chunk_file(filename, size=1024*512):
    chunks = []
    with open(filename, "rb") as f:
        i = 0
        while chunk := f.read(size):
            name = f"{filename}.part{i}"
            with open(name, "wb") as c:
                c.write(chunk)
            chunks.append(name)
            i += 1
    return chunks

def upload_chunk(chunk_name, peer_host, peer_port):
    with socket.socket() as s:
        s.connect((peer_host, peer_port))
        s.send(f"UPLOAD|{chunk_name}".encode())
        # wait for peer's READY acknowledgment
        ack = s.recv(1024).decode()
        if ack != "READY":
            print(f"[ALICE] Unexpected ack: {ack}")
            return
        # send file data in chunks
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


def main():
    filename = IMAGE_NAME
    chunks = chunk_file(filename)
    
    for i, chunk in enumerate(chunks):
        peer_host, peer_port = PEERS[i % len(PEERS)]
        upload_chunk(chunk, peer_host, peer_port)
        register_chunk(chunk, filename, peer_port)


    print("[ALICE] Upload and registration complete.")

if __name__ == "__main__":
    main()
# alice.py
# This script is responsible for chunking a file and uploading each chunk to a peer.
# It also registers each chunk with the tracker server.
# It connects to the tracker server to register the chunks and their respective peers.
# It connects to the peers to upload the chunks.
# The script uses a round-robin approach to distribute the chunks among the available peers.
# The script uses a fixed chunk size of 512 KB.
# The script uses a simple socket connection to communicate with the tracker and peers.