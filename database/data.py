"""
    DATA
"""
import os
import pandas as pd

def load_csv_data():
    """
        This function import the hospital data from the csv file.
    """
    # project directory returning an absolute path
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "hospitaldata.csv")

    hospital_df = pd.read_csv(csv_path)
    return hospital_df
