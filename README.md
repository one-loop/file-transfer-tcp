
# How to Run the File Distribution Code 📋

Follow these steps:

1. **Run the Tracker**  
   Open a terminal and run:
   ```bash
   python3 tracker.py
   ```

2. **Run the Peers**  
   Open separate terminals for each peer and run:
   ```bash
   python3 peer.py 7001
   ```
   ```bash
   python3 peer.py 7002
   ```
   (will create two peers running on ports 7001 and 7002 respectively)

3. **Upload the File with Alice**  
   In another terminal, run:
   ```bash
   python3 alice.py
   ```

4. **Download and Reconstruct the File with Bob**  
   Finally, in another terminal, run:
   ```bash
   python3 bob.py
   ```
   Bob will download the chunks from the registered peers and reconstruct the file.
   The file should appear in the current working directory as reconstructed_[filename.extension]
