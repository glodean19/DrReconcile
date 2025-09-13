"""
   Importing the modules
"""
from database.ethnicity import load_ethnicity
from database.sexual_orientation import load_so
from database.hospital import load_hospital
from database.patient import load_patient
from database.data import load_csv_data
from database.registration import load_registration


def main():
    """
        This is the main function calling loading 
        the other functions in a specific order,
        based on the database schema and relationships.
    """
    hospital_df = load_csv_data()
    load_ethnicity()
    load_so()
    load_hospital(hospital_df)
    load_patient()
    load_registration()


if __name__=="__main__":
    main()
