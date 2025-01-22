import json
import os

# Path to your JSON file where messages will be saved
MESSAGE_FILE_PATH = "messages.json"

def save_message_to_file(message_data):
    # Check if the file exists, if not, create it
    if not os.path.exists(MESSAGE_FILE_PATH):
        with open(MESSAGE_FILE_PATH, 'w') as file:
            json.dump([], file)  # Initialize with an empty list if file doesn't exist

    # Read existing messages from the file
    with open(MESSAGE_FILE_PATH, 'r') as file:
        messages = json.load(file)

    # Append the new message to the list
    messages.append(message_data)

    # Write the updated messages back to the file
    with open(MESSAGE_FILE_PATH, 'w') as file:
        json.dump(messages, file, indent=4)
