import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


def generate_epr_documents_data(num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month):
    """
    Generate dummy data for the 'epr_documents' index.

    Parameters:
    - num_rows (int): Number of rows to generate.
    - entered_list (list): List of entered values.
    - global_start_year (int): Start year for the global date range.
    - global_start_month (int): Start month for the global date range.
    - global_end_year (int): End year for the global date range.
    - global_end_month (int): End month for the global date range.

    Returns:
    - pd.DataFrame: Generated DataFrame with specified columns.
    """
    current_pat_client_id_code = random.choice(entered_list)

    data = {
        'client_idcode': [random.choice(entered_list) for _ in range(num_rows)],
        'document_guid': [f'doc_{i}' for i in range(num_rows)],
        'document_description': [f'description_{i}' for i in range(num_rows)],
        'body_analysed': [fake.paragraph() for _ in range(num_rows)],
        'updatetime': [datetime(
            random.randint(global_start_year, global_end_year),
            random.randint(global_start_month, global_end_month),
            random.randint(1, 28),
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        ) for _ in range(num_rows)],
        'clientvisit_visitidcode': [f'visit_{i}' for i in range(num_rows)]
    }

    df = pd.DataFrame(data)
    return df


def generate_epr_documents_personal_data(num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month):
    """
    Generate dummy data for the 'epr_documents' index with linked personal information.

    Parameters:
    - num_rows (int): Number of rows to generate.
    - entered_list (list): List of entered values.
    - global_start_year (int): Start year for the global date range.
    - global_start_month (int): Start month for the global date range.
    - global_end_year (int): End year for the global date range.
    - global_end_month (int): End month for the global date range.

    Returns:
    - pd.DataFrame: Generated DataFrame with linked personal information.
    """
    current_pat_client_id_code = random.choice(entered_list)

    data = {
        'client_idcode': [current_pat_client_id_code] * num_rows,
        'client_firstname': [fake.first_name() for _ in range(num_rows)],
        'client_lastname': [fake.last_name() for _ in range(num_rows)],
        'client_dob': [fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d') for _ in range(num_rows)],
        'client_gendercode': [random.choice(['male', 'female']) for _ in range(num_rows)],
        'client_racecode': [fake.random_element(['Caucasian', 'African American', 'Hispanic', 'Asian', 'Other']) for _ in range(num_rows)],
        'client_deceaseddtm': [fake.date_time_this_decade() if random.choice([True, False]) else None for _ in range(num_rows)],
        'updatetime': [datetime(
            random.randint(global_start_year, global_end_year),
            random.randint(global_start_month, global_end_month),
            random.randint(1, 28),
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        ) for _ in range(num_rows)]
    }

    df = pd.DataFrame(data)
    return df


def generate_observations_data(num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month):
    """
    Generate dummy data for the 'observations' index.

    Parameters:
    - num_rows (int): Number of rows to generate.
    - entered_list (list): List of entered values.
    - global_start_year (int): Start year for the global date range.
    - global_start_month (int): Start month for the global date range.
    - global_end_year (int): End year for the global date range.
    - global_end_month (int): End month for the global date range.

    Returns:
    - pd.DataFrame: Generated DataFrame with specified columns.
    """
    current_pat_client_id_code = random.choice(entered_list)

    data = {
        'observation_guid': [f'obs_{i}' for i in range(num_rows)],
        'client_idcode': [random.choice(entered_list) for _ in range(num_rows)],
        'obscatalogmasteritem_displayname': 'AoMRC_ClinicalSummary_FT',
        'observation_valuetext_analysed': [fake.paragraph() for _ in range(num_rows)],
        'observationdocument_recordeddtm': [datetime(
            random.randint(global_start_year, global_end_year),
            random.randint(global_start_month, global_end_month),
            random.randint(1, 28),
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        ) for _ in range(num_rows)],
        'clientvisit_visitidcode': [f'visit_{i}' for i in range(num_rows)]
    }

    df = pd.DataFrame(data)
    return df


def generate_basic_observations_data(num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month):
    """
    Generate dummy data for the 'basic_observations' index.

    Parameters:
    - num_rows (int): Number of rows to generate.
    - entered_list (list): List of entered values.
    - global_start_year (int): Start year for the global date range.
    - global_start_month (int): Start month for the global date range.
    - global_end_year (int): End year for the global date range.
    - global_end_month (int): End month for the global date range.

    Returns:
    - pd.DataFrame: Generated DataFrame with specified columns.
    """
    current_pat_client_id_code = random.choice(entered_list)

    data = {
        'client_idcode': [current_pat_client_id_code] * num_rows,
        'basicobs_itemname_analysed': [' '.join(fake.words(nb=random.randint(1, 2))) for _ in range(num_rows)],
        'basicobs_value_numeric': [random.uniform(1, 100) for _ in range(num_rows)],
        'basicobs_entered': [datetime(
            random.randint(global_start_year, global_end_year),
            random.randint(global_start_month, global_end_month),
            random.randint(1, 28),
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        ) for _ in range(num_rows)],
        'clientvisit_serviceguid': [f'service_{i}' for i in range(num_rows)]
    }

    df = pd.DataFrame(data)
    return df


def cohort_searcher_with_terms_and_search_dummy(index_name, fields_list, term_name, entered_list, global_start_year, global_start_month, global_end_year, global_end_month, search_string):
    """
    Generate dummy data based on the provided index and search parameters. This function is a dummy for a real cogStack deployment. 

    Parameters:
    - index_name (str): Name of the index.
    - fields_list (list): List of fields for the DataFrame columns.
    - term_name (str): Term name for search.
    - entered_list (list): List of entered values.
    - global_start_year (int): Start year for the global date range.
    - global_start_month (int): Start month for the global date range.
    - global_end_year (int): End year for the global date range.
    - global_end_month (int): End month for the global date range.
    - search_string (str): Search string for additional filtering.

    Returns:
    - pd.DataFrame: Generated DataFrame based on the specified conditions.
    """
    if "client_firstname" in fields_list:
        # You can adjust the number of rows as needed
        num_rows = random.randint(0, 10)
        df = generate_epr_documents_personal_data(
            num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month)
        return df
    elif "basicobs_value_numeric" in search_string:
        # You can adjust the number of rows as needed
        num_rows = random.randint(0, 10)
        df = generate_basic_observations_data(
            num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month)
        return df
    elif index_name == "epr_documents":
        # You can adjust the number of rows as needed
        num_rows = random.randint(0, 10)
        df = generate_epr_documents_data(
            num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month)
        return df
    elif index_name == "observations":
        # You can adjust the number of rows as needed
        num_rows = random.randint(0, 10)
        df = generate_observations_data(
            num_rows, entered_list, global_start_year, global_start_month, global_end_year, global_end_month)
        return df
    else:
        print(f"Index name is not 'epr_documents', 'observations', 'basic_observations'. Returning an empty DataFrame.")
        return pd.DataFrame(columns=['updatetime'] + fields_list)


# # Example usage for epr_documents with personal information:
# epr_documents_personal_df = cohort_searcher_with_terms_and_search_dummy(
#     index_name="epr_documents",
#     fields_list=["client_idcode", "client_firstname", "client_lastname", "client_dob", "client_gendercode", "client_racecode", "client_deceaseddtm", "updatetime"],
#     term_name="client_idcode.keyword",
#     entered_list=['D3232DUM23'],  # Add more client IDs as needed
#     global_start_year=2022,
#     global_start_month=1,
#     global_end_year=2023,
#     global_end_month=12,
#     search_string=f'updatetime:[{global_start_year}-{global_start_month} TO {global_end_year}-{global_end_month}]'
# )

# display(epr_documents_personal_df)
