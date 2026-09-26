import argon2 as argon2id
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import database

Type = argon2id.low_level.Type
hash_secret_raw = argon2id.low_level.hash_secret_raw
ph = argon2id.PasswordHasher()


# Create the key to encrypt and decrypt database

def derive_key(master_password: str, salt: bytes, tc, mc, p, kl) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode("utf-8"),
        salt=salt,
        time_cost=tc,
        memory_cost=mc,
        parallelism=p,
        hash_len=kl,
        type=Type.ID,
    )

# Get the metadata from the .vault file

def get_data():
    package = json.load(open("./passwords.vault", encoding="utf-8"))
    return {
        "version": package["version"],
        "salt": base64.b64decode(package["salt"]),
        "nonce": base64.b64decode(package["nonce"]),
        "ciphertext": base64.b64decode(package["ciphertext"]),
        "memory_kib": package["memory_kib"],
        "time_cost": package["time_cost"],
        "parallelism": package["parallelism"],
        "key_length": package["key_length"]
    }

# Encrypt database

def encrypt(master_password: str, connection) -> bool:
    plaintext = database.serialize(connection)
    metadata = get_data()

    version = metadata["version"] + 1
    salt = metadata["salt"]
    time_cost = metadata["time_cost"]
    memory_kib = metadata["memory_kib"]
    parallelism = metadata["parallelism"]
    key_length = metadata["key_length"]
    nonce = os.urandom(12)
    key = derive_key(master_password, salt, time_cost, memory_kib, parallelism, key_length)

    # This is the encrypted database
    ciphertext = AESGCM(key).encrypt(
        nonce,
        plaintext,
        None
    )

    # Metadata
    package = {
        "version": version,
        "memory_kib": memory_kib,
        "time_cost": time_cost,
        "parallelism": parallelism,
        "key_length": key_length,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }

    # Write into the .vault file.
    with open("./passwords.vault.tmp", "w", encoding="utf-8") as f:
        json.dump(package, f)
    os.replace("./passwords.vault.tmp", "./passwords.vault")
    del plaintext, metadata, connection, salt, nonce, ciphertext
    return True

# Decrypt database

def decrypt(master_password: str) -> bool:
    metadata = get_data()

    # encryption data
    salt = metadata["salt"]
    nonce = metadata["nonce"]
    ciphertext = metadata["ciphertext"]
    # parameters
    time_cost = metadata["time_cost"]
    memory_kib = metadata["memory_kib"]
    parallelism = metadata["parallelism"]
    key_length = metadata["key_length"]

    try:
        key = derive_key(master_password, salt, time_cost, memory_kib, parallelism, key_length)
        db = AESGCM(key).decrypt(nonce, ciphertext, None)
    except:
        return False

    connection = database.open_db(db)
    del db
    return connection

def setup(master_password):
    is_first_time = json.load(open("./passwords.vault", encoding="utf-8"))["ciphertext"]
    if is_first_time == "":
        connection = database.create_db()
        plaintext = database.serialize(connection)

        # Metadata
        version = 0
        salt = ph.hash(os.urandom(16)).encode('utf-8')
        nonce = os.urandom(12)
        time_cost = 3
        memory_kib = 65536
        parallelism = 4
        key_length = 32
        key = derive_key(master_password, salt, time_cost, memory_kib, parallelism, key_length)

        # Encrypt database
        ciphertext = AESGCM(key).encrypt(
            nonce,
            plaintext,
            None
        )

        # Write the vault file
        package = {
            "version": version,
            "memory_kib": memory_kib,
            "time_cost": time_cost,
            "parallelism": parallelism,
            "key_length": key_length,
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        }

        with open("./passwords.vault", "w", encoding="utf-8") as f:
            json.dump(package, f)
        return True
    else:
        return False