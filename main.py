from utility import install_packages

# Install necessary packages
install_packages(["Faker", "pandas"])

from controllers import AppController
import json

def load_schema(json_file):
    """
    Load the database schema from a JSON file.
    
    Args:
    json_file (str): Path to the JSON file containing the schema.
    
    Returns:
    dict: The loaded schema.
    """
    with open(json_file, 'r') as file:
        return json.load(file)


def main():
    # Load the schema from the JSON file
    schema = load_schema('schema.json')
    
    # Initialize the AppController with the loaded schema
    controller = AppController(schema)
   
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