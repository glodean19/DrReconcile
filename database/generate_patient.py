"""
    HELPER FUNCTION
"""
import random
from datetime import datetime
from faker import Faker

# It uses the Faker library to simulate patient names,
# date of birth (DOB), and date of death (DOD).
fake = Faker()
Faker.seed(0)
random.seed(0)

ethnicity_values = [
    "White", "Mixed", "Asian", "Black",
    "Other", "Don't know", "Unknown", "None"
]

sexual_orientation_values = [
    "Heterosexual", "Gay", "Bisexual", "Other", "Don't know", "Prefer not to say"
]

def generate_dob_and_dod():
    """
    This function creates a DOB within a 100 year age range 
    and assigns a DOD with a 30% probability.
    """
    dob = fake.date_of_birth(minimum_age=0, maximum_age=100)
    dod = None
    # 30% chance of being deceased
    if random.random() < 0.3:
        # it generates a random year of death at least 1 year after birth,
        # not exceeding 100 years of age or today
        dod_year = dob.year + random.randint(1, max(1, min(100, datetime.now().year - dob.year)))
        try:
            dod = datetime(dod_year, dob.month, dob.day)
            # dob can't be greater than today
            if dod > datetime.now():
                dod = None
        # 70% of the time → still alive
        except ValueError:
            dod = None
    return dob, dod

def generate_patient(i):
    """
        his function constructs a single patient record with fields like title, 
        first/middle/last name, gender-based conditional fields like 
        previous_lastname (for females), a unique NHS number, 
        age (calculated from DOB and DOD or current date), 
        and foreign keys for ethnicity and sexual orientation. 
        It generates 100 patient records as a DataFrame.
    """
    dob, dod = generate_dob_and_dod()
    age = (dod or datetime.now()).year - dob.year

    # gender has been generated to help assigning previous last names
    gender = fake.random_element(["M", "F"])
    # 70% chance the person has a middle name
    middle_name = fake.first_name() if random.random() < 0.7 else None
    # If the person is female, there's a 50% chance they have a previous last name (maiden name)
    previous_last_name = fake.last_name() if gender == "F" and random.random() < 0.5 else None

    return {
        # patientid starting from 1000
        "patientid": 1000 + i,
        "title": fake.prefix(),
        "firstname": fake.first_name(),
        "middlename": middle_name,
        "lastname": fake.last_name(),
        "previous_lastname": previous_last_name,
        # 10 dg NHSNumber
        "nhsnumber": str(9000000000 + i),
        "dob": dob,
        "dod": dod,
        "age": age,
        # ethnicity and sexual orientation hardcoded to simulate inconsistent data
        "ethnicity": random.choice(ethnicity_values),
        "sexual_orientation": random.choice(sexual_orientation_values)
    }
