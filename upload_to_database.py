import streamlit_authenticator as stauth

import database as db

usernames = ["admin", "muh_asmann"]
names = ["admin", "muhammad asman"]
passwords = ["12345678", "admin123"]
hashed_passwords = stauth.Hasher(passwords).generate()


for (username, name, hash_password) in zip(usernames, names, hashed_passwords):
    db.insert_user(username, name, hash_password)
