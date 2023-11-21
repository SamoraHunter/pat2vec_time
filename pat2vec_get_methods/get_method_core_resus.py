import numpy as np
import pandas as pd

from util.methods_get import (filter_dataframe_by_timestamp,
                              get_start_end_year_month)


def get_core_resus(current_pat_client_id_code, target_date_range, pat_batch, batch_mode=False, cohort_searcher_with_terms_and_search=None):
    """
    Retrieves CORE_RESUS_STATUS features for a given patient within a specified date range.

    Parameters:
    - current_pat_client_id_code (str): The client ID code of the patient.
    - target_date_range (tuple): A tuple representing the target date range.
    - pat_batch (pd.DataFrame): The DataFrame containing patient data.
    - batch_mode (bool, optional): Indicates whether batch mode is enabled. Defaults to False.
    - cohort_searcher_with_terms_and_search (callable, optional): The function for cohort searching. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing CORE_RESUS_STATUS features for the specified patient.
    """
    start_year, start_month, end_year, end_month, start_day, end_day = get_start_end_year_month(target_date_range)

    if batch_mode:
        current_pat_raw = filter_dataframe_by_timestamp(pat_batch, start_year, start_month, end_year, end_month, start_day, end_day, 'observationdocument_recordeddtm')
    else:
        current_pat_raw = cohort_searcher_with_terms_and_search(
            index_name="observations",
            fields_list=["observation_guid", "client_idcode", "obscatalogmasteritem_displayname", "observation_valuetext_analysed", "observationdocument_recordeddtm", "clientvisit_visitidcode"],
            term_name="client_idcode.keyword",
            entered_list=[current_pat_client_id_code],
            search_string="obscatalogmasteritem_displayname:(\"CORE_RESUS_STATUS\") AND " + f'observationdocument_recordeddtm:[{start_year}-{start_month}-{start_day} TO {end_year}-{end_month}-{end_day}]'
        )

    if len(current_pat_raw) == 0:
        features = pd.DataFrame(data={'client_idcode': [current_pat_client_id_code]})
    else:
        features_data = current_pat_raw[current_pat_raw['obscatalogmasteritem_displayname'] == 'CORE_RESUS_STATUS'].copy()

        term = 'core_resus_status'.lower()
        features = pd.DataFrame(data={'client_idcode': [current_pat_client_id_code]})

        if not features_data.empty:
            features[f'{term}_For_cardiopulmonary_resuscitation'] = len(features_data[features_data['observation_valuetext_analysed'] == 'For cardiopulmonary resuscitation'])
            features[f'{term}_Not_for_cardiopulmonary_resuscitation'] = len(features_data[features_data['observation_valuetext_analysed'] == 'Not for cardiopulmonary resuscitation'])
        else:
            features[f'{term}_For_cardiopulmonary_resuscitation'] = 0
            features[f'{term}_Not_for_cardiopulmonary_resuscitation'] = 0

    return features

