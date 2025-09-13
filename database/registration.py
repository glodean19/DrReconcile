"""
    REGISTRATION TABLE
"""
import random
from datetime import timedelta
import pandas as pd
from faker import Faker
from database.engine import get_engine

fake = Faker()

def generate_registration(registration_id,
                          patient_id,
                          hospital_ids,
                          status_options,
                          admission_reasons):
    """
        HELPER FUNCTION
    """
    # fake date within the last 60 days
    reg_date = fake.date_between(start_date='-60d', end_date='today')
    # fake date discharge in the last 30 days
    dis_date = fake.date_between(start_date='-30d', end_date='today')

    # if the discharge is before the registration,
    # it'll add random number of days to a series of datetime values
    if dis_date < reg_date:
        dis_date = reg_date + timedelta(days=random.randint(1, 5))

    # It returns a single fake registration record as a dictionary
    return {
        "registrationid": registration_id,
        "dateregistration": reg_date,
        "registrationstatus": random.choice(status_options),
        "datedischarge": dis_date,
        "patientid": patient_id,
        "orgid": random.choice(hospital_ids),
        "reason_for_admission": random.choice(admission_reasons)
    }

def load_registration():
    """
        This function will load the registrations in the table with
        patientid and hospitalid in their renge and lists of statuses 
        and medical issues. Each patient gets at least one registration,
        starting from id 6000 and incrementing. Some patients have an extra
        medical issue chosen by adding a weight to the chances: 50% for 0 extra,
        30% to 1 extra, 20% to 2 extra. For each record there is a random chance to
        get an extra registration. All records are converted in a dataframe and
        appended to the registration table.
    """
    patient_ids = list(range(1000, 2000))
    hospital_ids = list(range(1, 395))
    status_options = ['standard', 'unknown patient', 'remotely registered']
    admission_reasons = [
        "Chest pain", "Abdominal pain", "Shortness of breath", "Fever", "Cough",
        "Headache", "Dizziness", "Fracture", "Infection", "Seizure",
        "Mental health crisis", "Hypertension", "Diabetes complications",
        "Back pain", "Pregnancy-related issue", "Post-surgical complication",
        "Skin rash", "Allergic reaction", "Vomiting", "Unexplained weight loss",
        "Trauma", "Dehydration", "Burns", "Stroke", "Heart attack",
        "Palpitations", "Anemia", "Loss of consciousness", "Drug overdose", 
        "Alcohol intoxication","Gastrointestinal bleeding", "Constipation", 
        "Diarrhea", "Asthma exacerbation", "Kidney stones",
        "Hematuria (blood in urine)", "Joint pain", "Swelling of limbs", 
        "Hearing loss", "Vision changes", "Tachycardia", "Bradycardia", 
        "Panic attack", "Chest injury", "Foreign body ingestion"
    ]

    registrations = []
    reg_id = 6000

    # Ensure every patient has at least one registration
    for pid in patient_ids:
        registrations.append(generate_registration(reg_id,
                                                   pid,
                                                   hospital_ids,
                                                   status_options,
                                                   admission_reasons))
        reg_id += 1

        # Random chance of having more registrations
        extra_regs = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
        # _ (variable name). the loop will iterate n times, not a classic iteration counter
        for _ in range(extra_regs):
            registrations.append(generate_registration(reg_id,
                                                       pid,
                                                       hospital_ids,
                                                       status_options,
                                                       admission_reasons))
            reg_id += 1

    # Convert to DataFrame
    registration_df = pd.DataFrame(registrations)

    engine = get_engine()
    registration_df.to_sql("registration",
                           engine,
                           if_exists="append",
                           index=False)

    print("Registration data inserted successfully.")

    # Return the DataFrame
    return registration_df
