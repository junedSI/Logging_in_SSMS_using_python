import unittest
from unittest.mock import MagicMock
from Logging_in_python.logger import Logger
import datetime

class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.log_file = "test.log"
        self.server = "localhost"
        self.database = "testdb"
        self.username = "testuser"
        self.password = "testpass"
        self.tablename = "Logs"
        self.logger = Logger(self.log_file, self.server, self.database, self.username, self.password, self.tablename)
        self.logger.cursor = MagicMock()
        self.logger.conn = MagicMock()

    def tearDown(self):
        self.logger.close_connection()
        self.logger = None

    def test_check_table_existing(self):
        """Test the check_table method when the table already exists in the database."""
        # Mock the result of the table existence check to True
        self.logger.cursor.execute.return_value = True

        self.logger.check_table()

        self.logger.cursor.execute.assert_called_once()
        self.logger.conn.commit.assert_not_called()
        print("Table exists")

    def test_check_table_non_existing(self):
        """Test the check_table method when the table does not exist in the database."""
        # Mock the result of the table existence check to False
        self.logger.cursor.execute.return_value = False

        self.logger.check_table()

        self.logger.cursor.execute.assert_called_once()
        self.logger.conn.commit.assert_called_once()
        print("Table created successfully")

    def test_log_local_error(self):
        """Test the log_local_error method."""
        timestamp = datetime.datetime.now()
        log_level = "error"
        source_filename = "test_file.py"
        source_module = "test_module"
        source_function = "test_function"
        source_line = 10
        message = "Test error message"

        self.logger.log_local_error(timestamp, log_level, source_filename,
                                    source_module, source_function, source_line, message)

        with open(self.log_file, "r") as file:
            log_content = file.read()
            self.assertIn(message, log_content)

    def test_log_dataDB(self):
        """Test the log_dataDB method."""
        timestamp = datetime.datetime.now()
        log_level = "info"
        source_filename = "test_file.py"
        source_module = "test_module"
        source_function = "test_function"
        source_line = 20
        message = "Test info message"

        self.logger.log_dataDB(timestamp, log_level, source_filename,
                               source_module, source_function, source_line, message)

        self.logger.cursor.execute.assert_called_once()
        self.logger.conn.commit.assert_called_once()

    def test_log_message(self):
        """Test the log_message method."""
        level = "debug"
        message = "Test debug message"

        self.logger.connect_to_database = MagicMock()

        self.logger.log_message(level, message)

        timestamp = datetime.datetime.now()
        frame = self.logger.log_message.__code__.co_consts[5].co_code
        source_filename = "logger.py"
        source_module = "logger"
        source_function = "log_message"
        source_line = 91
        log_level = level.upper()

        self.logger.connect_to_database.assert_called_once_with(timestamp, log_level, source_filename,
                                                                source_module, source_function, source_line, message)
        self.logger.log_dataDB.assert_called_once_with(timestamp, log_level, source_filename,
                                                       source_module, source_function, source_line, message)

if __name__ == "__main__":
    unittest.main()