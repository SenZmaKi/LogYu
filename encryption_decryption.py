from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os

def generate_keys(path: str):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    private_key_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
    public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    with open(os.path.join(path, "private_key.pem"), "wb") as f:
        f.write(private_key_pem)
    with open(os.path.join(path, "public_key.pem"), "wb") as f:
        f.write(public_key_pem)

def load_private_key(path: str, password=None)-> rsa.RSAPrivateKey:
    with open(os.path.abspath(path), "rb") as f:
        return serialization.load_pem_private_key(f.read(), password)

def load_public_key(path: str)-> rsa.RSAPublicKey:
    with open(os.path.abspath(path), "rb") as f:
        return serialization.load_pem_public_key(f.read())
    
def encrypt(message: bytes, public_key: rsa.RSAPublicKey)-> bytes:
    return public_key.encrypt(message,
                       padding.OAEP(
                            mgf=padding.MGF1(hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                       ))

def decrypt (message: bytes, private_key: rsa.RSAPrivateKey)->bytes:
    return private_key.decrypt(message,
                       padding.OAEP(
                            mgf=padding.MGF1(hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                       ))
# message = "Amogus"
# print("Original message: ", message)
# encrypted_message = encrypt(message.encode(), load_public_key("./public_key.pem"))
# print("Encrypted message: ", encrypted_message)
# print("Decrypted message: ", decrypt(encrypted_message, load_private_key("./private_key.pem")).decode())