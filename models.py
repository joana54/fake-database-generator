import sqlite3
from faker import Faker
import random

class Database:
    """
    The Database class handles the creation and management of an in-memory SQLite database.
    It also generates and inserts fake data into the database tables based on a provided schema.
    """

    def __init__(self, schema, config):
        """
        Initialize the Database object.

        :param schema: List[dict] - A schema defining the structure of the database tables.
        """
        # Initialize the in-memory SQLite database
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
        self.cursor = self.conn.cursor()
        self.fake = Faker()  # Initialize Faker for generating fake data
        self.schema = schema  # Store the schema for table creation and data insertion
        self.config = config # Store the config settings

        # Set random seed if specified
        if "random_seed" in config:
            random.seed(config["random_seed"])
            Faker.seed(config["random_seed"])

        self.create_tables()  # Create tables based on the schema

    def create_tables(self):
        """
        Create tables in the database based on the provided schema.

        This method reads the schema and constructs the necessary SQL statements
        to create the tables with appropriate fields and constraints (e.g., primary keys, foreign keys).
        """
        for table in self.schema:
            fields = []
            foreign_keys = []
            for field in table["fields"]:
                # Define each field in the table
                field_definition = f'{field["name"]} {field["type"]}'
                if field.get("primary_key", False):
                    field_definition += " PRIMARY KEY"
                if field.get("unique", False):
                    field_definition += " UNIQUE"
                if "foreign_key" in field:
                    # Define foreign key constraints
                    foreign_keys.append(f'FOREIGN KEY ({field["name"]}) REFERENCES {field["foreign_key"]["references"]}')
                fields.append(field_definition)
           
            # Combine field definitions with foreign key constraints
            fields_sql = ", ".join(fields + foreign_keys)
            create_table_sql = f'CREATE TABLE {table["table_name"]} ({fields_sql})'
            self.cursor.execute(create_table_sql)  # Execute the SQL to create the table

    def generate_fake_data(self):
        """
        Generate and insert fake data into the database tables based on the schema.

        This method generates 10 rows of fake data for each table using the Faker library
        and inserts the data into the database. It also handles foreign key relationships
        and ensures uniqueness where required.
        """
        id_references = {}  # Dictionary to store generated IDs for foreign key references
        used_user_ids = set()  # Set to track used user IDs for uniqueness

        for table in self.schema:
            num_records = self.config["num_records"].get(table["table_name"], 10)
            # Prepare the SQL insert statement for the current table
            insert_sql = f'INSERT INTO {table["table_name"]} ({", ".join([f["name"] for f in table["fields"] if "fake_data" in f or "foreign_key" in f])}) VALUES ({", ".join(["?" for f in table["fields"] if "fake_data" in f or "foreign_key" in f])})'
            fake_data_rows = []
            for _ in range(num_records):  # Generate 10 rows of fake data
                row = []
                for field in table["fields"]:
                    if "fake_data" in field:
                        # Generate fake data based on the specified type
                        fake_value = self.generate_fake_value(field["fake_data"])
                        row.append(fake_value)
                    elif "foreign_key" in field:
                        # Handle foreign key references
                        referenced_table, referenced_field = field["foreign_key"]["references"].split("(")
                        referenced_field = referenced_field.rstrip(")")
                        # Ensure uniqueness for 1-to-1 relationships
                        if "unique" in field:
                            available_user_ids = [id for id in id_references[referenced_table] if id not in used_user_ids]
                            if available_user_ids:
                                foreign_key_value = random.choice(available_user_ids)
                                used_user_ids.add(foreign_key_value)
                            else:
                                continue  # Skip or break if no more unique IDs are available
                        else:
                            foreign_key_value = random.choice(id_references[referenced_table])
                    
                        row.append(foreign_key_value)
                    elif field.get("primary_key", False):
                        continue  # Skip primary keys if they're auto-incremented
                fake_data_rows.append(tuple(row))

            # Execute the insert statement and track primary keys if needed
            self.cursor.executemany(insert_sql, fake_data_rows)

            # Track generated IDs if this table has a primary key
            if any(f.get("primary_key", False) for f in table["fields"]):
                id_references[table["table_name"]] = [row[0] for row in self.cursor.execute(f'SELECT {table["fields"][0]["name"]} FROM {table["table_name"]}').fetchall()]

        self.conn.commit()  # Commit the transaction

    def generate_fake_value(self, fake_data_type):
        """
        Generate a fake value based on the specified type.

        :param fake_data_type: str - The type of fake data to generate.
        :return: The generated fake value.
        """
        # Check if Faker has the requested method and use it
        if hasattr(self.fake, fake_data_type):
            return getattr(self.fake, fake_data_type)()
        elif fake_data_type == "random_float":
            return round(random.uniform(5.0, 500.0), 2)
        elif fake_data_type == "random_int":
            return random.randint(1, 10)
        # Add more data types as needed here

    def fetch_data(self, table_name):
        """
        Fetch all data from the specified table.

        :param table_name: str - The name of the table to fetch data from.
        :return: List[tuple] - A list of tuples containing the rows of data.
        """
        return self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()

    def close(self):
        """
        Close the database connection.

        This method ensures that the connection to the SQLite database is properly closed,
        freeing up any resources that were being used.
        """
        self.conn.close()
