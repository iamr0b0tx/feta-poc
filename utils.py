import os.path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def generate_key_pair(working_dir):
    private_key = ec.generate_private_key(ec.SECP384R1())

    with open(os.path.join(working_dir, "private"), 'wb') as file:
        file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(os.path.join(working_dir, "public"), 'wb') as file:
        file.write(private_key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        ))


def main():
    # create feta key pair
    generate_key_pair("feta/dump/peer1/")
    generate_key_pair("feta/dump/peer2/")

    # create social key pair
    generate_key_pair("social/dump/peer1/")
    generate_key_pair("social/dump/peer2/")
