from models import Database
from views import Display

class AppController:
    def __init__(self, schema):
        # Initialize the AppController with a database schema
        self.db = Database(schema)
   
    def generate_data(self):
        # Generate fake data in the database
        self.db.generate_fake_data()
   
    def show_table(self, table_name):
        # Fetch data from the database for the specified table
        data = self.db.fetch_data(table_name)
        # Find the schema for the specified table
        table_schema = next(table for table in self.db.schema if table["table_name"] == table_name)
        # Extract column names from the table schema
        columns = [field["name"] for field in table_schema["fields"]]
        # Display the table data using the Display class
        Display.show_table(data, columns, table_name)
   
    def close_db(self):
        # Close the database connection
        self.db.close()