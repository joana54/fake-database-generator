"""
This module contains the AppController class, which orchestrates the interaction between the 
data management (handled by the Database class) and the data presentation (handled by the 
Display class) components of the application. It manages core functionalities such as initiating 
data generation, fetching data for display, and closing database connections.

Classes:
    AppController: Manages database operations & coordinates with the Display class to show data.

The AppController integrates the application's data layer with its presentation layer, 
providing a high-level interface for database interaction and data visualization.
"""

from models import Database
from views import Display

class AppController:
    """
    The AppController class serves as the intermediary between the data layer (Database)
    and the presentation layer (Display). It manages database operations and data display
    using the provided schema.
    """

    def __init__(self, schema, config):
        """
        Initialize the AppController with a database schema and configuration.

        Args:
            schema (list of dict): Database schema.
            config (dict): Configuration parameters.
        """
        self.db = Database(schema, config)

    def generate_data(self):
        """
        Generate and insert fake data into the database using the schema.
        
        This method relies on the `generate_fake_data` method of the Database class
        to create mock data for testing or demonstration purposes.
        """
        # Generate fake data in the database
        self.db.generate_fake_data()

    def show_table(self, table_name):
        """
        Fetch and display data from the specified table.

        :param table_name: str - The name of the table whose data is to be fetched and displayed.
        
        This method performs the following steps:
        1. Fetches data from the database for the specified table.
        2. Extracts column names from the table schema.
        3. Displays the data using the Display class.
        """
        # Fetch data for the specified table from the database
        data = self.db.fetch_data(table_name)

        # Find the schema for the specified table
        table_schema = next(table for table in self.db.schema if table["table_name"] == table_name)

        # Extract column names from the table schema
        columns = [field["name"] for field in table_schema["fields"]]

        # Display the table data using the Display class
        Display.show_table(data, columns, table_name)

    def close_db(self):
        """
        Close the database connection.

        This method ensures that the connection to the database is properly closed,
        freeing up any resources that were being used.
        """
        # Close the database connection
        self.db.close()
