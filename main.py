"""
This module is designed to manage database interactions and data manipulation for a specific 
application. It provides functions to load JSON schema and configuration files, initialize 
the application controller, generate fake data within the database, display data, and close 
the database connection efficiently.

Functions:
    load_schema(json_file): Load and return the database schema from a JSON file.
    load_config(json_file): Load and return the configuration parameters from a JSON file.
    main(): Orchestrates the database schema loading, data generation, display, and cleanup.

This module serves as the entry point of the script, utilizing the AppController to handle 
all database operations.
"""

import json
from utility import install_packages
from controllers import AppController

# Install necessary packages using the custom utility function
install_packages(["Faker", "pandas"])

def load_schema(json_file):
    """
    Load the database schema from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing the schema.

    Returns:
        dict: The loaded schema.
    """
    with open(json_file, mode='r', encoding="utf-8") as file:
        return json.load(file)


def load_config(json_file):
    """
    Load the configuration parameters from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing the configuration.

    Returns:
        dict: The loaded configuration.
    """
    with open(json_file, mode='r', encoding="utf-8") as file:
        return json.load(file)

def main():
    """
    Main function that orchestrates the loading of the schema, data generation,
    data display, and cleanup (closing the database connection).

    This function follows these steps:
    1. Load the database schema from a JSON file.
    2. Initialize the AppController with the loaded schema.
    3. Generate fake data in the database.
    4. Display data for each table defined in the schema.
    5. Close the database connection.
    """
    # Load the schema from the JSON file
    schema = load_schema('schema.json')

    # Load the configuration from the JSON file
    config = load_config('config.json')

    # Initialize the AppController with the loaded schema and configuration
    controller = AppController(schema, config)

    # Generate fake data in the database
    controller.generate_data()

    # Display data for each table in the schema
    for table in schema:
        controller.show_table(table["table_name"])

    # Close the database connection
    controller.close_db()

# Entry point of the script
if __name__ == "__main__":
    main()
