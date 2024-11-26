import secrets

def generate_api_key():
    api_key = secrets.token_hex(32)  # Generates a 64-character hexadecimal API key
    print(f"Generated API Key: {api_key}")  # Print the API key to the console
    return api_key

# Call the function to test
if __name__ == "__main__":
    generate_api_key()

# import secrets

# # Generate a 32-byte secure random secret key
# secret_key = secrets.token_hex(32)

# print(f"Your secret key is: {secret_key}")
