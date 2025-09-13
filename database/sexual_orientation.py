"""
    SEXUAL_ORIENTATION TABLE
"""
import pandas as pd
from database.engine import get_engine

def load_so():
    """
        This function first defines a list of the sexual orientation categories, 
        then creates a pandas DataFrame assigning each one a unique id starting from 3000. 
        After creating the DataFrame, the function establishes the database connection and 
        appends the data into the sexual_orientation table using the to_sql method.
        NHS sexual orientation data from this link:
        https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-sets/mental-health-services-data-set/submit-data/data-quality-of-protected-characteristics-and-other-vulnerable-groups/sexual-orientation
    """
    # Define the 6 sexual orientation categories
    so_categories = [
        "Straight or Heterosexual",
        "Gay or Lesbian",
        "Bisexual",
        "All other sexual orientations",
        "Not answered",
        "Does not apply"
    ]

    # Create DataFrame
    so_df = pd.DataFrame({
        "soid": [3000 + i for i in range(len(so_categories))],
        "soname": so_categories
    })

    engine = get_engine()
    so_df.to_sql("sexual_orientation",
                 engine,
                 if_exists="append",
                 index=False)

    print("SO data inserted successfully.")
