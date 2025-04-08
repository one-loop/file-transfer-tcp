import os
import socket

port = 5069
# create a TCP client internet socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", port)) # create local host socket port

# open the file and find the file size to send to the receiver
file = open("image.png", "rb")
file_size = os.path.getsize("image.png")

# send the file size and file name to the receiver
client.send("received_image.png".encode())
client.send(str(file_size).encode())

# read the file data and send it to the receiver
data = file.read()
client.sendall(data)
client.send(b"<EOF>") # send end of file signal to the receiver
print("file sent successfully")

# close the file and client socket
file.close()
client.close()
