import socket
import tqdm

port = 5069
# create a TCP server internet socket at the receiving end
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", port)) # create local host socket port and bind to it
server.listen()
print(f"Server Listening on Port {port}...")

# accept a single client from the server
client, addr = server.accept()

# get the file name from the sender
file_name = client.recv(1024).decode()
# get the file size from the sender
file_size = client.recv(1024).decode()

print(f"Receiving {file_name} from {addr} ({file_size} bytes)")

file = open(file_name, "wb")

file_bytes = b""

done = False

# create a progress bar to show the file transfer progress
progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))
while not done:
    # read the file data from the sender
    data = client.recv(1024)
    if file_bytes[-5:] == b"<EOF>": # check for end of file signal
        done = True
        data = data.replace(b"<EOF>", b"")
    else:
        # add the data to the file bytes
        file_bytes += data

    # update the rpogress bar
    progress.update(len(data)) # update the progress bar

file.write(file_bytes) # write the file bytes to the file
file.close() # close the file

# close the client and server sockets
client.close()
server.close()

print(f"File {file_name} received successfully")