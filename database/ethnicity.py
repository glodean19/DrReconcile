"""
   ETHNICITY TABLE
"""
import pandas as pd
from database.engine import get_engine


def load_ethnicity():
    """
    This function populates the ethnicity table with the national ethnicity code and description 
    extracted from the NHS website. It creates a dataframe with id starting from 5000 
    and it appends the records in the database after enstablishing the connection.
    NHS Ethnicity from the following link:
    https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-sets/mental-health-services-data-set/submit-data/data-quality-of-protected-characteristics-and-other-vulnerable-groups/ethnicity
    """
    # Hardcoded EthnicCode and Description pairs from the National code
    ethnicity_descriptions = [
        ("A", "White - British"),
        ("B", "White - Irish"),
        ("C", "White - Any other White background"),
        ("D", "Mixed - White and Black Caribbean"),
        ("E", "Mixed - White and Black African"),
        ("F", "Mixed - White and Asian"),
        ("G", "Mixed - Any other mixed background"),
        ("H", "Asian or Asian British - Indian"),
        ("J", "Asian or Asian British - Pakistani"),
        ("K", "Asian or Asian British - Bangladeshi"),
        ("L", "Asian or Asian British - Any other Asian background"),
        ("M", "Black or Black British - Caribbean"),
        ("N", "Black or Black British - African"),
        ("P", "Black or Black British - Any other Black background"),
        ("R", "Other Ethnic Groups - Chinese"),
        ("S", "Other Ethnic Groups - Any other ethnic group"),
        ("Z", "Not stated"),
        ("99", "Not known"),
    ]

    # Create the DataFrame
    ethnicity_df = pd.DataFrame([
        {
            "ethnicityid": 5000 + i,
            "ethniccode": code,
            "description": desc
        }
        for i, (code, desc) in enumerate(ethnicity_descriptions)
    ])

    # Insert into the "ethnicity" table (append mode, don't overwrite)
    engine = get_engine()
    ethnicity_df.to_sql("ethnicity",
                        engine,
                        if_exists="append",
                        index=False)

    print("Ethnicity data inserted successfully.")
