# Python Password Manager
A simple local password manager made with Python and SQLite.
This project helped me learn about encryption, usage of SQL databases in Python and the bytes type.

## Usage
Firstly, install the required libraries by executing ``pip install -r requirements.txt`` in your terminal. Once all the required libraries are installed, use ``python3 passwdmgr.py setup``, this creates the necessary previous structure for the app to work properly. You will be prompted to create a password, this password will be used every time you want to access the password manager to identify you, make a secure password keep it well stored.

Start the program with ``python3 passwdmgr.py``, this displays the help. There are two options: add a new password and see a stored password.

To add a new password use ``python3 passwdmgr.py add``. After typing your master password, you will be prompted to create the entry for your password: title, username, password, URL of the service the login is for (optional) and notes (optional).

To see the entry of an existing login use ``python3 passwdmgr.py get``. After typing your master password, you can search for a login by its title, the manager will return the details of the found login or tell you if it doesn't exist.
