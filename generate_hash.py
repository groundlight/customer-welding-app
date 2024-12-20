import bcrypt
import argparse


def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Generate the hashed password
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()  # Store as a string


parser = argparse.ArgumentParser(description="Hash a password")
parser.add_argument("password", help="The password to hash")
args = parser.parse_args()

password = args.password

# Generate hashed password
hashed_password = hash_password(password)

print(f"Hashed password: {hashed_password}")
