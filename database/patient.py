"""
    PATIENT TABLE
"""

import pandas as pd
from database.engine import get_engine
from database.generate_patient import generate_patient

def load_patient():
    """
        This function calls the generate_patient helper function 1000 times, 
        passing a unique index each time to create individual patient records with fake data. 
        All the records are collected into a list and converted into a pandas DataFrame. 
        The function then uses a SQLAlchemy engine, to append the DataFrame 
        into the patient table using the to_sql method.
    """
    # call the helper function to generate 1000 patient records
    patients = [generate_patient(i) for i in range(1000)]
    df_patients = pd.DataFrame(patients)

    engine = get_engine()
    df_patients.to_sql("patient",
                       engine,
                       if_exists="append",
                       index=False)

    print("Patient data inserted successfully.")
