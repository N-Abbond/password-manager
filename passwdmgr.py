import sys
import database
import vault


# Functions

def authenticate():
    master_key = input("Type your master password: ")
    connection = vault.decrypt(master_key)

    if not connection:
        print("Invalid password")
        return False, False
    else:
        return master_key, connection

def not_blank(message):
    var = ""
    is_blank = not var.strip()
    while is_blank:
        var = input(message)
        is_blank = not var.strip()
        if is_blank:
            print("Can't leave this field blank")
            continue
    return var


# Main program

def main():
    # If no arguments were provided

    if len(sys.argv) <= 1 or sys.argv[1] == 'help':
        print("""Usage: python3 passwdmgr.py [command]
Replace [command] with one of two options
    'add' to create a new entry
    'get' to retrieve username, password and notes (if exist) from entry with provided name
    'setup' to create password (only for the first time)
    'help' to display this help""")
        return 0

    # If too many arguments
    if len(sys.argv) > 2:
        print("Too many arguments, type 'help' to display guide")
        return 1

    # If invalid arguments
    if not ['add', 'get', 'setup'].__contains__(sys.argv[1]):
        print("Invalid arguments, type 'help' to display guide")
        return 1

    command = sys.argv[1]

    # Setup

    if command == 'setup':
        master_key = input("Type your password (make a memorable or password store it securely): ")
        success = vault.setup(master_key)
        if success:
            print("Setup complete\nUse the help command for information on usage")
        else:
            create_new = input("The vault contains passwords, are you sure you want to create a new manager?\nTHIS WILL DELETE ALL YOUR PREVIOUS PASSWORDS (y/n): ")
            if create_new.lower() == "y":
                success = vault.setup(master_key)
                print("Setup complete\nUse the help command for information on usage")
            elif create_new.lower() == "n":
                print("Abort.")
                return 0
            else:
                print(f"'{create_new}' is not a valid option. Abort.")
                return 0
            return 0


    # Authenticate and decrypt vault

    connection = None
    master_key = None
    vault_open = False

    try:
        master_key, connection = authenticate()
        if not master_key:
            return 1

        vault_open = True


        # Add a new entry

        if command == 'add':
            print("To leave an empty field, just press enter")
            title = not_blank("Name (not blank): ")
            username = input("Username: ")
            password = not_blank("Password (not blank): ")
            url = input("Service URL: ")
            notes = input("Notes: ")

            entry = {
                "title": title,
                "username": username,
                "password": password,
                "url": url,
                "notes": notes
            }
            result, used = database.add_password(entry, connection)
            print("\n")
            print(result)

            # Exit
            vault.encrypt(master_key, connection)
            vault_open = False
            return(0)


        # Get password

        if command == 'get':
            # pending: display all entry names, type one to display its contents
            title = input("Search by title: ")

            password, used = database.get_password(title, connection)

            print("\n") # Display results
            if password is None:
                password = "There's no such entry: " + title

            if used:
                print("Showing results of: " + used)

            print(password)

            # Exit
            vault.encrypt(master_key, connection)
            vault_open = False
            return 0


    finally:
        if vault_open:
            vault.encrypt(master_key, connection)
            vault_open = False

        master_key = None


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(130)