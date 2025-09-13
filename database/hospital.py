"""
    HOSPITAL TABLE
"""
from database.engine import get_engine

def load_hospital(hospital_df):
    """
        The function uses the hospital_df dataframe from the 
        imported CSV file. It first renames the columns to match 
        the corresponding schema of the hospital table in the database. 
        It then adds a new column, orgid, assigning each row a unique ID starting from 0001. 
        After reordering the columns, the function uses a SQLAlchemy engine 
        to append the data into the hospital table using the to_sql method.
    """
    # Rename csv columns to match the database schema
    hospital_df.rename(columns={
        "Name": "orgname",
        "Address 1": "orgaddressline1",
        "Address 2": "orgaddressline2",
        "Address 3": "orgaddressline3",
        "City": "orgcity",
        "Country": "orgcountry",
        "PostCode": "orgpostcode"
    }, inplace=True)

    # Add incremental OrgID starting from 0001
    hospital_df["orgid"] = range(1, len(hospital_df) + 1)

    # Reorder columns to match the table schema
    hospital_df = hospital_df[["orgid",
                               "orgname",
                               "orgaddressline1",
                               "orgaddressline2",
                               "orgaddressline3",
                               "orgcity",
                               "orgcountry",
                               "orgpostcode"]]

    engine = get_engine()
    hospital_df.to_sql("hospital",
                       engine,
                       if_exists="append",
                       index=False)

    print("Hospital data inserted successfully.")
