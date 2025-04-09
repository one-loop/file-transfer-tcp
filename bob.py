# bob.py
import socket
import json
import os

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000
IMAGE_NAME = "img2.jpg"


def get_chunk_list(filename):
    with socket.socket() as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        s.send(f"GET|{filename}".encode())
        data = s.recv(4096).decode()
        return json.loads(data)

def download_chunk(chunk_name, peer_host, peer_port):
    with socket.socket() as s:
        s.connect((peer_host, peer_port))
        s.send(f"SEND|{chunk_name}".encode())
        with open(chunk_name, "wb") as f:
            while True:
                data = s.recv(4096)
                if not data:
                    break
                f.write(data)


def reconstruct_file(output_file, chunk_names):
    # Sort using the numeric part after 'part'
    sorted_chunks = sorted(chunk_names, key=lambda name: int(name.rsplit("part", 1)[-1]))
    print("Reconstructing the File")
    with open(output_file, "wb") as f:
        for chunk in sorted_chunks:
            print(chunk)
            with open(chunk, "rb") as c:
                f.write(c.read())

def main():
    filename = IMAGE_NAME
    chunk_list = get_chunk_list(filename)
    print(chunk_list)

    chunk_names = []
    
    for chunk_name, peer_host, peer_port in chunk_list:
        print(f"[BOB] Downloading {chunk_name} from {peer_host}:{peer_port}")
        download_chunk(chunk_name, peer_host, peer_port)
        chunk_names.append(chunk_name)

    reconstruct_file("reconstructed_" + filename, chunk_names)
    print("[BOB] File reconstruction complete.")

if __name__ == "__main__":
    main()
