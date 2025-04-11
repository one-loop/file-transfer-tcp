import socket
import json
import os

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000

def get_chunk_list(filename):
    # connect to the tracker and request the list of chunks for the given filename
    # the tracker will respond with a list of tuples (chunk_name, peer_host, peer_port)
    # e.g. [("image.png.part0", "localhost", 7001), ("image.png.part1", "localhost", 7002), ...]
    with socket.socket() as s:
        # create a socket and connect to the tracker, and send a GET request to the tracker for the filename
        s.connect((TRACKER_HOST, TRACKER_PORT))
        s.send(f"GET|{filename}".encode())
        # receive the response (list of chunks of the file) from the tracker
        data = s.recv(4096).decode()
        # the response is a JSON string, so we need to parse it into a Python object (list of tuples)
        # e.g. [("image.png.part0", "localhost", 7001), ("image.png.part1", "localhost", 7002), ...]
        return json.loads(data)

def download_chunk(chunk_name, peer_host, peer_port):
    # connect to the peer and send a SEND request to the peer for the chunk
    with socket.socket() as s:
        s.connect((peer_host, peer_port))
        s.send(f"SEND|{chunk_name}".encode())
        with open(chunk_name, "wb") as f:
            # receive the chunk data from the peer and write it to a file
            while True:
                data = s.recv(4096)
                if not data:
                    break
                f.write(data)

def reconstruct_file(output_file, chunk_names):
    # sort using the numeric part after 'part'. This is important to ensure the file is reconstructed in the correct order
    sorted_chunks = sorted(chunk_names, key=lambda name: int(name.rsplit("part", 1)[-1]))
    print("Reconstructing the File")
    # open the output file in binary mode and write all the chunks to it
    with open(output_file, "wb") as f:
        for chunk in sorted_chunks:
            if os.path.exists(chunk):  # Ensure the chunk exists before attempting to open it
                with open(chunk, "rb") as c:
                    f.write(c.read())
            else:
                print(f"[BOB] Warning: Chunk {chunk} does not exist. Skipping...")

    # delete the chunk files after reconstruction
    for chunk in sorted_chunks:
        if os.path.exists(chunk):
            os.remove(chunk)
        else:
            print(f"[BOB] Warning: Chunk {chunk} not found for removal.")

def main():
    # get the filename to be downloaded
    while True:
        filename = input("Enter file name: ")
        chunk_list = get_chunk_list(filename)
        if not chunk_list:
            print("[BOB] File not found. Please try again.")
        else:
            break

    chunk_names = []
    
    # download each chunk from their respective peers and store in separate files
    for chunk_name, peer_host, peer_port in chunk_list:
        print(f"[BOB] Downloading {chunk_name} from {peer_host}:{peer_port}")
        download_chunk(chunk_name, peer_host, peer_port)
        # add the chunk name to the list of chunk names, which will be used to reconstruct the file
        chunk_names.append(chunk_name)

    # Ask for the name of the reconstructed file (without extension)
    base_name = input("Enter name for the reconstructed file (without extension): ")

    # Automatically retrieve the extension from the first chunk and add it to the base name
    # Assuming all chunks have the same extension
    extension = chunk_names[0].split('.')[-2]  # Get the file extension from the chunk name
    output_filename = f"{base_name}.{extension}"  # Combine base name with extension

    # reconstruct the file from all the downloaded chunks
    reconstruct_file(output_filename, chunk_names)
    print(f"[BOB] File reconstruction complete: {output_filename}")

if __name__ == "__main__":
    main()