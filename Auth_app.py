from Logging_in_python.logger import Logger
import time
import re
import os


def read_credentials_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        data = [line.strip() for line in lines]
    return data


credentials_file_path = os.path.join('cred.txt')

# Fetch the credentials from the file
fetched_credentials = read_credentials_from_file(credentials_file_path)

# Pass the fetched credentials to the Logger object
log_file = fetched_credentials[0]
server = fetched_credentials[1]
database = fetched_credentials[2]
username = fetched_credentials[3]
password = fetched_credentials[4]
tablename = fetched_credentials[5]

logger = Logger(log_file, server, database, username, password, tablename)


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def register(users):
        start_time = time.time()
        username = input("Enter a username: ")
        password = input("Enter a password: ")

        if not username.strip() or not password.strip():
            logger.log_message("error", "Blank username or password submitted")
            print("Error: Username and password cannot be blank.")
            return

        logger.log_message("debug", "Registering user: {}".format(username))

        if not re.match(r"[^@]+@gmail\.com$", username):
            logger.log_message(
                "warning", "Invalid username format: {}".format(username))
            print("Invalid username! Please enter a Gmail address.")
            return

        if username[0] in "!@#$%^&*()-+?_" or password[0] in "!@#$%^&*()-+?_":
            logger.log_message(
                "warning", "Invalid username or password format")
            print(
                "Invalid username or password! They should not start with a special character.")
            return

        user = User(username, password)
        users.append(user)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.log_message("info", "User registered: {}. Time taken: {} seconds".format(
            username, elapsed_time))
        logger.log_message("debug", "Registration process ended")
        print("Registration successful!")

    @staticmethod
    def login(users):
        start_time = time.time()

        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if not username.strip() or not password.strip():
            logger.log_message("error", "Blank username or password submitted")
            print("Error: Username and password cannot be blank.")
            return

        logger.log_message("debug", "Logging in user: {}".format(username))

        for user in users:
            if user.username == username and user.password == password:
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.log_message("info", "User logged in: {}. Time taken: {} seconds".format(
                    username, elapsed_time))
                logger.log_message("debug", "Login process ended")
                print("Login successful!")
                return

        logger.log_message(
            "warning", "Invalid login attempt: {}".format(username))
        logger.log_message("debug", "Login process ended")
        print("Invalid username or password.")


def main():
    users = []
    while True:
        print("\nUser Authentication System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            logger.log_message("debug", "Registration process started")
            User.register(users)
        elif choice == "2":
            logger.log_message("debug", "Login process started")
            User.login(users)
        elif choice == "3":
            print("Exiting the program...")
            logger.log_message("info", "Program exited")
            break
        else:
            logger.log_message("warning", "Invalid choice: {}".format(choice))
            print("Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
