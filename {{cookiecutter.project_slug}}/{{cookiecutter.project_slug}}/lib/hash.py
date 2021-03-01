import bcrypt

EXPECTED_SALT_LENGTH = 29
ENCODING = 'utf-8'


def hash_plaintext(plaintext: str, salt: bytes = None):
    if not salt:
        salt = bcrypt.gensalt()

    return (bcrypt.hashpw(plaintext.encode(ENCODING), salt).decode(ENCODING),
            salt.decode(ENCODING))


def compare_plaintext_to_hash(plaintext: str, hashed_plaintext: str,
                              salt: str = None):
    if not salt:
        salt = hashed_plaintext[:EXPECTED_SALT_LENGTH]

    new_hashed_plaintext = bcrypt.hashpw(plaintext.encode(ENCODING),
                                         salt.encode(ENCODING))
    return new_hashed_plaintext == hashed_plaintext.encode(ENCODING)
