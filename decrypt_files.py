import encryption_decryption
import pathlib
import os

root_script_path = "./"

encrypted_files_folder_path = os.path.abspath(os.path.join(root_script_path, "logged_files"))
private_key_path = os.path.abspath(os.path.join(root_script_path, "private_key.pem"))
decrypted_files_folder_path = os.path.abspath(os.path.join("d3crypt3d")) 
decrypted_file_extension = ".txt"

private_key = encryption_decryption.load_private_key(private_key_path)

encrypted_files = pathlib.Path(encrypted_files_folder_path).glob("*")

if not os.path.isdir(decrypted_files_folder_path): os.mkdir(decrypted_files_folder_path)
for file in encrypted_files:
    with open(file, "rb") as f:
        data = f.read()
        if data:
            decrypted = encryption_decryption.decrypt(data, private_key)
            with open(os.path.join(decrypted_files_folder_path, file.name+decrypted_file_extension), "wb") as f:
                f.write(decrypted)

