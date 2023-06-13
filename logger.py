import pyodbc
import datetime
import inspect

class Logger:
    def __init__(self, log_file, server, database, username, password, tablename):
        """
        Initialize the Logger object.
        Args:
            log_file (str): Path to the log file.
            server (str): Server name.
            database (str): Database name.
            username (str): Username for the database connection.
            password (str): Password for the database connection.
            tablename (str): Name of the table to store logs.
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.tablename = tablename
        self.log_file = log_file
        self.conn = None
        self.cursor = None

    def connect_to_database(self, timestamp, log_level, source_filename,
                            source_module, source_function, source_line, message):
        """
        Connect to the database and check if the table exists. If not, create the table.
        Args:
            timestamp (datetime.datetime): Timestamp of the log entry.
            log_level (str): Log level of the message.
            source_filename (str): Filename of the source code where the log message is originated.
            source_module (str): Module name of the source code.
            source_function (str): Function name of the source code.
            source_line (int): Line number in the source code.
            message (str): Log message content.
        """
        try:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            # print("Connected")
            self.check_table()

        except pyodbc.Error:
            self.log_local_error(timestamp, log_level, source_filename,
                                 source_module, source_function, source_line, message)

    def check_table(self):
        """
        Check if the table exists in the database. If not, create the table.
        This function uses the information_schema to check the table existence.
        Note: It assumes that the tablename attribute is properly escaped and doesn't contain SQL injection vulnerabilities.
        """
        try:
            query = f"SELECT 1 FROM information_schema.tables WHERE table_name = '{self.tablename}'"
            result = self.cursor.execute(query)

            if result:
                print("Table exists")
            else:
                create_table_query = f"""
                CREATE TABLE {self.tablename} (
                    logID INT IDENTITY(1,1) PRIMARY KEY,
                    timestamp DATETIME, 
                    level VARCHAR(50), 
                    source_filename VARCHAR(100),
                    source_module VARCHAR(100),
                    source_function VARCHAR(100),
                    source_line INT,
                    message TEXT
                )
                """
                self.cursor.execute(create_table_query)
                self.conn.commit()
                # print("Table created successfully")
                # we should do common exception handdeling so that the parent function can get it. either do a raise  

        except pyodbc.Error as e:
            print(f"Error occurred: {str(e)}")

    def log_local_error(self, timestamp, log_level, source_filename,
                        source_module, source_function, source_line, message):
        """
        Log the message to a local file.
        Args:
            timestamp (datetime.datetime): Timestamp of the log entry.
            log_level (str): Log level of the message.
            source_filename (str): Filename of the source code where the log message is originated.
            source_module (str): Module name of the source code.
            source_function (str): Function name of the source code.
            source_line (int): Line number in the source code.
            message (str): Log message content.
        """
        log_message = f"{timestamp} {str(log_level).upper()} - {source_filename}::{source_module}::{source_function}::{source_line} - {message}"
        with open(self.log_file, "a") as file:
            file.write(log_message + "\n")

    def log_dataDB(self, timestamp, log_level, source_filename,
                   source_module, source_function, source_line, message):
        """
        Log the message to the database table.
        Args:
            timestamp (datetime.datetime): Timestamp of the log entry.
            log_level (str): Log level of the message.
            source_filename (str): Filename of the source code where the log message is originated.
            source_module (str): Module name of the source code.
            source_function (str): Function name of the source code.
            source_line (int): Line number in the source code.
            message (str): Log message content.
        """
        insert_query = f"INSERT INTO {self.tablename} (timestamp, level, source_filename, source_module, source_function, source_line, message) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(insert_query, (timestamp, log_level, source_filename,
                                           source_module, source_function, source_line, message))
        self.conn.commit()

    def log_message(self, level, message):
        """
        Log the message to the database table and/or a local file.
        Args:
            level (str): Log level of the message.
            message (str): Log message content.
        Note: The source code information is retrieved dynamically using the inspect module.
        """
        timestamp = datetime.datetime.now()
        frame = inspect.currentframe().f_back.f_back
        source_filename = inspect.getframeinfo(frame).filename
        source_module = inspect.getmodule(frame).__name__
        source_function = inspect.currentframe().f_back.f_code.co_name
        source_line = inspect.getframeinfo(frame).lineno

        log_level = level.upper()
        print(log_level)

        if self.conn is None:
            self.connect_to_database(timestamp, log_level, source_filename,
                                     source_module, source_function, source_line, message)

        if self.cursor:
            self.log_dataDB(timestamp, log_level, source_filename,
                            source_module, source_function, source_line, message)

    def close_connection(self):
        """
        Close the database connection.

        Note: This should be called when you're done with logging to release the resources.
        """
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()
