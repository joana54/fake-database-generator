import pandas as pd

class Display:
    @staticmethod
    def show_table(data, columns, table_name):
        """
        Display the data in a tabular format using pandas DataFrame.

        Args:
        data (list of tuples): The data to be displayed.
        columns (list of str): The column names for the data.
        table_name (str): The name of the table being displayed.

        Returns:
        None
        """
        # Create a DataFrame from the data and columns
        df = pd.DataFrame(data, columns=columns)
        
        # Print the table name and the DataFrame
        print(f"\n{table_name}:\n", df)