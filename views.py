"""
This module defines the Display class, which is responsible for presenting data 
in a structured, tabular format. The class uses the pandas library to create and
show DataFrames, which allow for easy and readable display of tabular data.

Classes:
    Display: Offers functionality to display data tables using pandas DataFrames.

The module simplifies data presentation tasks across the application, especially
useful for debugging outputs, data analysis results, and reporting purposes.
"""

import pandas as pd

class Display:
    """
    The Display class provides static methods for displaying data in a tabular format.
    """

    @staticmethod
    def show_table(data, columns, table_name) -> None:
        """
        Display the data in a tabular format using a pandas DataFrame.

        Args:
            data (list of tuples): The data to be displayed. Each tuple represents a row.
            columns (list of str): The column names corresponding to the data.
            table_name (str): The name of the table being displayed.

        Returns:
            None
        """
        # Create a DataFrame from the data and columns
        df = pd.DataFrame(data, columns=columns)

        # Print the table name and the DataFrame
        print(f"\n{table_name}:\n", df)
