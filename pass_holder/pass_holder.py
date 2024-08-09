#!/usr/bin/env python3

import os
import subprocess
import getpass
from cryptography.fernet import Fernet
import base64
import hashlib
import random
import string
import time

# Utility function to generate a key from a seed phrase
def generate_key(seed_phrase: str) -> bytes:
    seed_phrase = seed_phrase.encode()  # Convert seed phrase to bytes
    key = hashlib.sha256(seed_phrase).digest()  # Hash the seed phrase
    return base64.urlsafe_b64encode(key[:32])  # Encode to base64

# Encrypt text
def encrypt_text(text: str, key: bytes) -> bytes:
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return encrypted_text

# Decrypt text
def decrypt_text(encrypted_text: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted_text = fernet.decrypt(encrypted_text)
    return decrypted_text.decode()

# Scramble text
def scramble_text(text: str) -> str:
    # Simple letter substitution for scrambling
    letters = string.ascii_letters
    scrambled = ''.join(random.choice(letters) if random.random() > 0.5 else char for char in text)
    return scrambled

# Function to print text with a delay
def print_with_delay(text: str, delay: float) -> None:
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Move to the next line after printing the text

# Function to handle the main logic
def main():
    # Clear the terminal screen
    os.system('clear')

    # Define colors
    ORANGE = '\033[33m'
    RESET = '\033[0m'

    # Generate and display the banner in orange with delay
    banner_text = "LEOPARD"
    figlet_command = f"figlet -f slant '{banner_text}'"
    figlet_output = subprocess.check_output(figlet_command, shell=True).decode('utf-8')

    print(f"{ORANGE}", end='')  # Set the color to orange
    print_with_delay(figlet_output, delay=0.009)
    print(f"{RESET}", end='')  # Reset the color

    filename = 'encrypted_file.txt'
    temp_filename = 'temp_file.txt'

    while True:
        if not os.path.exists(filename):
            print(f"File '{filename}' does not exist.")
            create_new = input("Do you want to create a new file? (yes/no): ").strip().lower()
            if create_new == 'yes':
                seed_phrase = getpass.getpass("Set a seed phrase for the new file: ")
                key = generate_key(seed_phrase)
                with open(filename, 'wb') as file:
                    file.write(b'')  # Create an empty file
                print("File created successfully.")
            else:
                print("Exiting.")
                break
        else:
            action = input("File exists. Do you want to (e)dit, (v)iew, or (x)exit? ").strip().lower()
            if action not in ['e', 'v', 'x']:
                print("Invalid option.")
                continue

            if action == 'x':
                print("Exiting.")
                break

            seed_phrase = getpass.getpass("Enter the seed phrase: ")
            key = generate_key(seed_phrase)

            try:
                with open(filename, 'rb') as file:
                    encrypted_data = file.read()
                decrypted_data = decrypt_text(encrypted_data, key)
            except Exception as e:
                # If decryption fails, scramble the text
                with open(filename, 'rb') as file:
                    encrypted_data = file.read()
                decrypted_data = scramble_text(encrypted_data.decode(errors='ignore'))
                print("Seed phrase is incorrect. Displaying scrambled text.")

            if action == 'e':
                # Save decrypted data to a temporary file
                with open(temp_filename, 'w') as file:
                    file.write(decrypted_data)

                # Open the temporary file in nano for editing
                subprocess.run(['nano', temp_filename], check=True)

                # After editing, read the content from the temporary file
                with open(temp_filename, 'r') as file:
                    edited_content = file.read()

                # Encrypt the updated content and save it back to the original file
                encrypted_content = encrypt_text(edited_content, key)
                with open(filename, 'wb') as file:
                    file.write(encrypted_content)

                # Remove the temporary file
                os.remove(temp_filename)

            elif action == 'v':
                print("File contents:")
                print(decrypted_data)

if __name__ == '__main__':
    main()

