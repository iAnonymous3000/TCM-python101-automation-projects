import hashlib
import argparse
import threading
from queue import Queue
import signal
import time

# Argument parser setup
parser = argparse.ArgumentParser(description='SHA256 Password Cracker')
parser.add_argument('hash', help='The SHA256 hash to crack')
parser.add_argument('password_file', help='File path to the password list')
args = parser.parse_args()

# Global variables
hash_to_crack = args.hash
password_file = args.password_file
attempts = 0
found = False

# Thread-safe print function
print_lock = threading.Lock()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global found
    print("\nExiting gracefully")
    found = True

signal.signal(signal.SIGINT, signal_handler)

# Function to perform SHA256 hashing
def sha256sum(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Worker function
def worker(password_queue):
    global attempts, found
    while not password_queue.empty() and not found:
        password = password_queue.get()
        password_hash = sha256sum(password)
        with print_lock:
            print(f"Attempt {attempts}: Trying password {password[:10]}...")
            attempts += 1
        if password_hash == hash_to_crack:
            with print_lock:
                print(f"Success! Password found: {password}")
            found = True
        password_queue.task_done()

# Main function
def main():
    # Create a queue for passwords
    password_queue = Queue()
    
    # Read the password file and fill the queue
    try:
        with open(password_file, 'r', encoding='utf-8') as f:
            for line in f:
                password = line.strip()
                password_queue.put(password)
    except FileNotFoundError:
        print(f"Error: The file {password_file} was not found.")
        return
    except IOError as e:
        print(f"IOError: {e}")
        return

    # Start worker threads
    thread_count = 4 # Number of threads to use
    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(password_queue,))
        t.daemon = True
        t.start()

    # Wait for the queue to be processed
    password_queue.join()

    if not found:
        print("Password not found in the list.")

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
