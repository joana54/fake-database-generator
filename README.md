# Fake Database Generator

A Python-based tool for dynamically generating relational databases with fake data, driven by a customizable JSON schema. Ideal for testing, prototyping, and simulating database interactions using an MVC architecture.

## Features

- **Dynamic Table Creation:** Define tables and relationships using a JSON schema.
- **Fake Data Generation:** Populate your database with realistic fake data using the Faker library.
- **Relational Integrity:** Enforces relationships between tables using foreign key constraints.
- **MVC Architecture:** Clean separation of concerns with Models, Views, and Controllers.
- **Customizable:** Easily modify the schema and data generation rules.

## Table of Contents

- [Usage](#usage)
- [Project Structure](#project-structure)
- [JSON Schema](#json-schema)
- [Example](#example)
- [Contributing](#contributing)

## Usage

1. **Define your schema:** Modify the `schema.json` file to match your desired database structure.
2. **Run the script:** Execute the main program to generate the database and display the tables.

```bash
python main.py
```

3. **View the results:** The generated tables and relationships will be displayed in the console or output format of your choice.

### Example Command

```bash
python main.py
```

This command generates the database based on the `schema.json` and populates it with fake data.

## Project Structure

```
fake-database-generator/
│
├── models.py         # Handles data structure and generation
├── views.py          # Handles data presentation
├── controllers.py    # Manages the flow between models and views
├── main.py           # Entry point for the application
├── schema.json       # JSON schema defining tables and relationships
└── requirements.txt  # Python dependencies
```

## JSON Schema

The `schema.json` file is the core configuration for this project. It defines the structure of your database, including tables, fields, and relationships.

### Example `schema.json`

```json
[
    {
        "table_name": "Users",
        "fields": [
            {"name": "user_id", "type": "INTEGER", "primary_key": true},
            {"name": "first_name", "type": "TEXT", "fake_data": "first_name"},
            {"name": "last_name", "type": "TEXT", "fake_data": "last_name"},
            {"name": "email", "type": "TEXT", "fake_data": "email"},
            {"name": "account_id", "type": "INTEGER", "foreign_key": {"references": "Accounts(account_id)"}, "unique": true},
            {"name": "order_id", "type": "INTEGER", "foreign_key": {"references": "Orders(order_id)"}},
        ]
    },
    ...
]
```

## Example

Suppose you want to create a database with `Users`, `Orders`, `Products`, and `OrderDetails` tables:

1. **Modify `schema.json`** with the required structure and relationships.
2. **Run `main.py`.**

The output will show the generated tables and their contents, with all relationships enforced.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue to improve this project.

### How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.
