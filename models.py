import sqlite3
from faker import Faker
import random

class Database:
    def __init__(self, schema):
        # Initialize the in-memory SQLite database
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
        self.cursor = self.conn.cursor()
        self.fake = Faker()  # Initialize Faker for generating fake data
        self.schema = schema  # Store the schema
        self.create_tables()  # Create tables based on the schema

    def create_tables(self):
        # Create tables based on the provided schema
        for table in self.schema:
            fields = []
            foreign_keys = []
            for field in table["fields"]:
                # Define each field in the table
                field_definition = f'{field["name"]} {field["type"]}'
                if field.get("primary_key", False):
                    field_definition += " PRIMARY KEY"
                if "foreign_key" in field:
                    # Define foreign key constraints
                    foreign_keys.append(f'FOREIGN KEY ({field["name"]}) REFERENCES {field["foreign_key"]["references"]}')
                fields.append(field_definition)
           
            # Combine field definitions with foreign key constraints
            fields_sql = ", ".join(fields + foreign_keys)
            create_table_sql = f'CREATE TABLE {table["table_name"]} ({fields_sql})'
            self.cursor.execute(create_table_sql)  # Execute the SQL to create the table

    def generate_fake_data(self):
        # Dictionary to store IDs for easy reference
        id_references = {}

        for table in self.schema:
            # Prepare the SQL insert statement
            insert_sql = f'INSERT INTO {table["table_name"]} ({", ".join([f["name"] for f in table["fields"] if "fake_data" in f or "foreign_key" in f])}) VALUES ({", ".join(["?" for f in table["fields"] if "fake_data" in f or "foreign_key" in f])})'
            fake_data_rows = []
            for _ in range(10):  # Generate 10 rows of fake data
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
        # Generate fake data based on the specified type
        if fake_data_type == "first_name":
            return self.fake.first_name()
        elif fake_data_type == "last_name":
            return self.fake.last_name()
        elif fake_data_type == "email":
            return self.fake.email()
        elif fake_data_type == "date_this_year":
            return self.fake.date_this_year()
        elif fake_data_type == "word":
            return self.fake.word()
        elif fake_data_type == "random_float":
            return round(random.uniform(5.0, 500.0), 2)
        elif fake_data_type == "random_int":
            return random.randint(1, 10)
        # Add more data types as needed

    def fetch_data(self, table_name):
        # Fetch all data from the specified table
        return self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()

    def close(self):
        # Close the database connection
        self.conn.close()