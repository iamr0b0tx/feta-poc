import json
from base64 import b64encode


def generate_key_pair():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    private_key = ec.generate_private_key(ec.SECP384R1())

    serialized_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    serialized_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    return serialized_private, serialized_public


def create_config(config, path):
    print(config)
    with open(path, 'w') as f:
        json.dump(config, f)


def create_peer1():
    private_key, public_key = generate_key_pair()
    create_config(
        {
            "principal_path": "dump/peer1/principal",
            "registry_url": "http://127.0.0.1:9000",
            "private_key": b64encode(private_key).decode("utf-8"),
            "public_key": b64encode(public_key).decode("utf-8")
        },
        "dump/peer1/config.json"
    )


def create_peer2():
    private_key, public_key = generate_key_pair()
    create_config(
        {
            "principal_path": "dump/peer2/principal",
            "registry_url": "http://127.0.0.1:9000",
            "private_key": b64encode(private_key),
            "public_key": b64encode(public_key)
        },
        "dump/peer2/config.json"
    )
