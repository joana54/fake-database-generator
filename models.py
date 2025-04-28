"""
This module contains the Database class, which is responsible for all direct interactions
with the SQLite database. It manages the creation and management of an in-memory database,
facilitates the generation and insertion of fake data based on a specified schema, and 
provides utilities for fetching and closing the database.

The Database class uses the SQLite3 library for database operations and the Faker library 
to generate realistic dummy data for testing or development purposes. It ensures that 
database operations are performed efficiently and safely, with support for foreign keys 
and data integrity.

Classes:
    Database: Handles the creation, manipulation, and querying of the SQLite database.
              It also manages connections and provides methods to close them properly.

The Database class is crucial for simulating a fully functional database environment 
during development, providing a robust platform for testing database-driven applications 
without the need for external database setups.
"""

import sqlite3
import random
import numpy as np
from datetime import datetime
from scipy.stats import truncnorm
from faker import Faker


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
        # Enable foreign key support
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.fake = Faker()  # Initialize Faker for generating fake data
        self.schema = schema  # Store the schema for table creation and data insertion
        self.config = config  # Store the config settings

        # Set random seed if specified
        if "random_seed" in config:
            random.seed(config["random_seed"])
            Faker.seed(config["random_seed"])

        self.create_tables()  # Create tables based on the schema

    def create_tables(self):
        """
        Create tables in the database based on the provided schema.
        """
        for table in self.schema:
            cols_sql = []
            table_fks = []
            single_pks = []
            composite_pk = None

            # Detect composite primary key definition
            if "composite_primary_keys" in table and table["composite_primary_keys"]:
                composite_pk = table["composite_primary_keys"][0]["fields"]

            for field in table["fields"]:
                parts = [field["name"], fld["type"]]

                if field.get("not_null", False):
                    parts.append("NOT NULL")

                if field.get("unique", False):
                    parts.append("UNIQUE")

                # In case if only one primary key column
                if composite_pk is None and field.get("primary_key", False):
                    parts.append("PRIMARY KEY")

                cols_sql.append(" ".join(parts))

                if composite_pk and field["name"] in composite_pk:
                    single_pks.append(field["name"])

            if composite_pk:
                cols_sql.append("PRIMARY KEY ({})".format(
                    ", ".join(composite_pk)))

            # Foreign‐keys handling
            for cfk in table.get("composite_foreign_keys", []):
                fk_fields = ", ".join(cfk["fields"])
                ref_table = cfk["references"]
                table_fks.append(
                    f"FOREIGN KEY ({fk_fields}) REFERENCES {ref_table}")

            all_defs = cols_sql + table_fks
            sql = f"CREATE TABLE {table['table_name']} (\n    " \
                + ",\n    ".join(all_defs) \
                + "\n);"

            self.cursor.execute(sql)

    def generate_fake_int_date(self):
        """
        Generate a fake date from 2000 up to today and return it as an int in 1YYMMDD format.
        Example: 2025-03-27 → 1250327
        """
        min_date = datetime(2000, 1, 1)
        max_date = datetime.today()

        fake_date = self.fake.date_between(
            start_date=min_date, end_date=max_date)

        century_digit = 1
        yy = fake_date.year % 100
        mm = fake_date.month
        dd = fake_date.day

        return int(f"{century_digit}{yy:02d}{mm:02d}{dd:02d}")

    def generate_fake_data(self):
        """
        Generate and insert fake data into the database, respecting foreign-key constraints.
        """
        id_references = {}

        parent_tables = [
            t for t in self.schema if "composite_primary_keys" in t]
        child_tables = [
            t for t in self.schema if "composite_foreign_keys" in t]

        # Insert into parent tables first
        for table in parent_tables:
            NUMERIC_TYPES = {"int", "float", "decimal", "bigint"}
            insertable_fields = [
                f for f in table["fields"]
                if "fake_data" in f or f.get("type", "").lower() in NUMERIC_TYPES
            ]
            columns = [f["name"] for f in insertable_fields]
            placeholders = ", ".join(["?"] * len(columns))
            insert_sql = f'INSERT INTO {table["table_name"]} ({", ".join(columns)}) VALUES ({placeholders})'

            # Generate rows
            fake_data_rows = []
            num_records = self.config["num_records"].get(
                table["table_name"], 10)
            for _ in range(num_records):
                row = []
                for field in insertable_fields:
                    if "fake_data" in field:
                        row.append(self.generate_fake_value(field))
                    else:  # numeric type
                        row.append(self.generate_fake_value(field))
                fake_data_rows.append(tuple(row))

            # Insert and commit
            self.cursor.executemany(insert_sql, fake_data_rows)
            self.conn.commit()

            pk_cols = [f["name"]
                       for f in table["fields"] if f.get("primary_key")]
            if pk_cols:
                id_references[table["table_name"]] = {}
                for pk in pk_cols:
                    rows = self.cursor.execute(
                        f"SELECT {pk} FROM {table['table_name']}"
                    ).fetchall()
                    id_references[table["table_name"]][pk] = [r[0]
                                                              for r in rows]

        # Insert into child tables
        for table in child_tables:
            # Determine composite foreign key fields and their parent table
            cfk = table["composite_foreign_keys"][0]
            fk_fields = cfk["fields"]
            parent_ref = cfk["references"].split("(")[0].strip()

            # Fetch valid composite key tuples from parent
            parent_key_cols = fk_fields
            placeholders = ", ".join(parent_key_cols)
            rows = self.cursor.execute(
                f"SELECT {placeholders} FROM {parent_ref}"
            ).fetchall()
            composite_keys = [tuple(r) for r in rows]

            NUMERIC_TYPES = {"int", "float", "decimal", "bigint"}
            insertable_fields = [
                f for f in table["fields"]
                if ("fake_data" in f or f.get("type", "").lower() in NUMERIC_TYPES or "foreign_key" in f)
                and f["name"] not in fk_fields
            ]

            # Final column order: non-foreign key fields, then foreign key fields
            columns = [f["name"] for f in insertable_fields] + fk_fields
            placeholders = ", ".join(["?"] * len(columns))
            insert_sql = f'INSERT INTO {table["table_name"]} ({", ".join(columns)}) VALUES ({placeholders})'

            # Generate rows
            fake_data_rows = []
            num_records = self.config["num_records"].get(
                table["table_name"], 10)
            for _ in range(num_records):
                row = []
                # Fill non-foreign key fields
                for field in insertable_fields:
                    if field.get("fake_data") or field.get("type", "").lower() in NUMERIC_TYPES:
                        row.append(self.generate_fake_value(field))
                    elif "foreign_key" in field:
                        # single-column foreign key: pick one of the parent's tracked primary keys
                        ref_table, ref_col = field["foreign_key"]["references"].split(
                            "(")
                        ref_col = ref_col.rstrip(")")
                        val = random.choice(id_references[ref_table][ref_col])
                        row.append(val)

                # Fill composite foreign keys fields by randomly picking one valid parent key
                co, sch, pl = random.choice(composite_keys)
                for fk in fk_fields:
                    if fk == "CoCode":
                        row.append(co)
                    elif fk == "SchCode":
                        row.append(sch)
                    elif fk == "PlanNo":
                        row.append(pl)
                    else:
                        idx = parent_key_cols.index(fk)
                        row.append((co, sch, pl)[idx])

                fake_data_rows.append(tuple(row))

            # Insert and commit child rows
            self.cursor.executemany(insert_sql, fake_data_rows)
            self.conn.commit()

    def generate_fake_value(self, field_info):
        """
        Generate a fake value based on the specified type.

        :param fake_data_type: str - The type of fake data to generate.
        :return: The generated fake value.
        """
        # Check for int-based date column
        if (
                field_info.get("type").lower() == "int"
                and "date" in field_info.get("name", "").lower()):
            return self.generate_fake_int_date()

        # Check if Faker has the requested method and use it
        if "fake_data" in field_info:
            fake_data_type = field_info["fake_data"]
            if hasattr(self.fake, fake_data_type):
                return getattr(self.fake, fake_data_type)()

        elif field_info.get("type").lower() in ["int", "float", "decimal", "bigint"]:
            try:
                mean = field_info.get("mean")
                std = field_info.get("stddev")
                min_val = field_info.get("min")
                max_val = field_info.get("max")

                if all(param is not None for param in [mean, std, min_val, max_val]):
                    if std == 0.0:
                        return mean
                    else:
                        a = (min_val - mean) / std
                        b = (max_val - mean) / std

                        sample = truncnorm.rvs(
                            a, b, loc=mean, scale=std, size=1)[0]
                        sample = np.clip(sample, min_val, max_val)

                        if field_info.get("type") in ["int", "bigint"]:
                            return int(round(sample))
                        return sample
            except (KeyError, ZeroDivisionError) as e:
                print(
                    f"Error generating numerical data for {field_info.get('name')}: {e}")

                if min_val is not None and max_val is not None:
                    if field_info.get("type") in ["int", "bigint"]:
                        return random.randint(min_val, max_val)
                    return random.uniform(min_val, max_val)
        return None

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
