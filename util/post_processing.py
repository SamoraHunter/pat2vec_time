import csv
import os
import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
import pandas as pd
from IPython.display import display
from tqdm import tqdm
import shutil
from typing import Optional, Union, Dict, List


sys.path.insert(0, '/home/aliencat/samora/gloabl_files')
sys.path.insert(0, '/data/AS/Samora/gloabl_files')
sys.path.insert(0, '/home/jovyan/work/gloabl_files')
sys.path.insert(0, '/home/cogstack/samora/_data/gloabl_files')


def count_files(path):
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(files)
    return count


def process_csv_files(input_path, out_folder='outputs', output_filename_suffix='concatenated_output',  part_size=336, sample_size=None, append_timestamp_column=False):
    """
    Concatenate multiple CSV files from a given input path and save the result to a specified output path.

    Parameters:
    - input_path (str): The path where the CSV files are located.
    - output_path (str): The path to save the concatenated CSV file.
    - out_folder (str): The folder name for the output CSV file. Default is 'outputs'.
    - output_filename_suffix (str): The suffix for the output CSV file name. Default is 'concatenated_output'.
    - curate_columns (bool): If True, use a curated list of columns. Default is False.
    - sample_size (int): Number of files to sample. If None, use all files. Default is None.
    - part_size (int): Size of parts for processing files in chunks. Default is 336.

    Returns:
    - None: The function saves the concatenated data to the specified output path.
    """

    curate_columns = False

    # Specify the directory where your CSV files are located
    all_file_paths = [os.path.join(dp, f) for dp, dn, filenames in os.walk(
        input_path) for f in filenames if os.path.splitext(f)[1] == '.csv']
    if type(sample_size) == str or sample_size == None:
        if (sample_size == None or sample_size.lower() == 'all'):
            sample_size = len(all_file_paths)

    # Create an output CSV file to hold the concatenated data
    output_file = os.path.join(
        out_folder, f'concatenated_data_{output_filename_suffix}.csv')

    # Keep track of all unique column names found across all CSV files
    unique_columns = set()

    # Sample files if sample_size is provided
    all_files = all_file_paths if sample_size is None else all_file_paths[:sample_size]

    # Create a dictionary to hold the concatenated data with the unique columns as keys
    concatenated_data = {column: [] for column in unique_columns}

    # Loop through each CSV file and read its data
    if not curate_columns:
        for file in (all_files):
            if file.endswith('.csv'):
                with open(file, 'r', newline='') as infile:
                    reader = csv.reader(infile)
                    try:
                        # Get the header of the current CSV file
                        header = next(reader)
                        # Add all column names to the unique_columns set
                        unique_columns.update(header)
                    except StopIteration:
                        pass

    # Check if the output file already exists
    if os.path.exists(output_file):
        # If it exists, append datetime stamp and "overwritten" to the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, extension = os.path.splitext(output_file)
        new_output_file = f"{base_name}_{timestamp}_overwritten{extension}"
        print(
            f"Warning: Output file already exists. Renaming {output_file} to {new_output_file}")
        os.rename(output_file, new_output_file)
    else:
        new_output_file = output_file

    # Create a header and write it to the output CSV file
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=unique_columns)
        writer.writeheader()

    # Loop through each CSV file again and concatenate its data to the dictionary
    for part_chunk in tqdm(range(0, len(all_files), part_size)):
        # Reset the concatenated_data dictionary for each part chunk
        concatenated_data = {column: [] for column in unique_columns}

        # Loop through each CSV file again and concatenate its data to the dictionary
        for file in all_files[part_chunk:part_chunk + part_size]:
            if file.endswith('.csv'):
                with open(file, 'r', newline='') as infile:
                    reader = csv.DictReader(infile)
                    # Loop through each row in the current CSV file
                    for row in reader:
                        # Add each value to the appropriate column in the dictionary
                        for column in unique_columns:
                            concatenated_data[column].append(
                                row.get(column, ''))

        # Append the concatenated data to the output CSV file
        with open(output_file, 'a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=unique_columns)
            for i in range(len(concatenated_data[next(iter(concatenated_data))])):
                writer.writerow(
                    {column: concatenated_data[column][i] for column in unique_columns})

    if (append_timestamp_column):
        print("Reading results and appending updatetime column")
        df = pd.read_csv(output_file)

        df = extract_datetime_to_column(df)

        df.to_csv(output_file)

    print(f"Concatenated data saved to {output_file}")

    return output_file

# Example Usage:
# concatenate_csv_files('/home/cogstack/samora/_data/HAEM_AG11193_3/new_project/current_pat_lines_parts', 'output_path_here')


def extract_datetime_to_column(df, drop=True):
    """
    Extracts datetime information from specified columns and creates a new column.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the datetime information in specific columns.

    Returns:
    - pandas.DataFrame: The DataFrame with a new column 'extracted_datetime_stamp' containing the extracted datetime values.
    """

    # Initialize the new column
    df['extracted_datetime_stamp'] = pd.to_datetime('')

    # Iterate through rows using tqdm for progress bar
    for index, row in tqdm(df.iterrows(), total=len(df)):
        # Iterate through columns
        for column in df.columns:
            # Check if the column contains '_date_time_stamp' and the value is 1
            if '_date_time_stamp' in column and row[column] == 1:
                # Extract date from column name and convert to datetime
                date_str = column.replace('_date_time_stamp', '')
                datetime_obj = pd.to_datetime(date_str, format='(%Y, %m, %d)')

                # Assign the datetime value to the new column
                df.at[index, 'extracted_datetime_stamp'] = datetime_obj

    # Display the count of extracted datetime values
    print(df['extracted_datetime_stamp'].value_counts())

    if (drop):
        columns_to_drop = [
            col for col in df.columns if 'date_time_stamp' in col]

        # Drop columns
        df = df.drop(columns=columns_to_drop)

    return df


def filter_annot_dataframe2(dataframe, filter_args):
    """
    Filter a DataFrame based on specified filter arguments.

    Parameters:
    - dataframe: pandas DataFrame
    - filter_args: dict
        A dictionary containing filter arguments.

    Returns:
    - pandas DataFrame
        The filtered DataFrame.
    """
    # Initialize a boolean mask with True values for all rows
    mask = pd.Series(True, index=dataframe.index)

    # Apply filters based on the provided arguments
    for column, value in filter_args.items():
        if column in dataframe.columns:
            # Special case for 'types' column
            if column == 'types':
                mask &= dataframe[column].apply(
                    lambda x: any(item.lower() in x for item in value))
            elif column in ['Time_Value', 'Presence_Value', 'Subject_Value']:
                # Include rows where the column is in the specified list of values
                mask &= dataframe[column].isin(value) if isinstance(
                    value, list) else (dataframe[column] == value)
            elif column in ['Time_Confidence', 'Presence_Confidence', 'Subject_Confidence']:
                # Include rows where the column is greater than or equal to the specified confidence threshold
                mask &= dataframe[column] >= value
            elif column in ['acc']:
                # Include rows where the column is greater than or equal to the specified confidence threshold
                mask &= dataframe[column] >= value
            else:
                mask &= dataframe[column] >= value

    # Return the filtered DataFrame
    return dataframe[mask]


def produce_filtered_annotation_dataframe(cui_filter=False, meta_annot_filter=False, pat_list=None, config_obj=None, filter_custom_args=None, cui_code_list=None, mct=False):
    """
    Filter annotation dataframe based on specified criteria.

    Parameters:
    - cui_filter (bool): Whether to filter by CUI codes.
    - meta_annot_filter (bool): Whether to apply meta annotation filtering.
    - pat_list (list): List of patient identifiers.
    - config_obj (ConfigObject): Configuration object containing necessary parameters.
    - filter_custom_args (dict): Custom filter arguments.
    - cui_code_list (list): List of CUI codes for filtering.

    Returns:
    - pd.DataFrame: Filtered annotation dataframe.
    """

    if meta_annot_filter:
        if filter_custom_args is None:
            print("Using config obj filter arguments..")
            filter_args = config_obj.filter_arguments
        else:
            filter_args = filter_custom_args

    results = []

    if pat_list is None:

        print("Using all patient list", len(config_obj.all_patient_list))
        pat_list = config_obj.all_patient_list

    for i in tqdm(range(len(pat_list))):
        current_pat_client_idcode = str(pat_list[i])

        if (mct == False):
            current_pat_annot_batch_path = config_obj.pre_document_annotation_batch_path + \
                current_pat_client_idcode + ".csv"
        else:
            current_pat_annot_batch_path = config_obj.pre_document_annotation_batch_path_mct + \
                current_pat_client_idcode + ".csv"

        if os.path.exists(current_pat_annot_batch_path):
            current_pat_annot_batch = pd.read_csv(current_pat_annot_batch_path)

            # drop nan on any col:
            necessary_columns = ['client_idcode', 'updatetime', 'pretty_name', 'cui', 'type_ids', 'types', 'source_value', 'detected_name',
                                 'acc', 'id', 'Time_Value', 'Time_Confidence', 'Presence_Value', 'Presence_Confidence', 'Subject_Value', 'Subject_Confidence']

            current_pat_annot_batch = current_pat_annot_batch.dropna(
                subset=necessary_columns)

            if meta_annot_filter:
                try:
                    current_pat_annot_batch = filter_annot_dataframe2(
                        current_pat_annot_batch, filter_args)
                except Exception as e:
                    print(e, i)
                    display(current_pat_annot_batch)
                    raise e

            if cui_filter:
                current_pat_annot_batch = current_pat_annot_batch[current_pat_annot_batch['cui'].isin(
                    cui_code_list)]

            results.append(current_pat_annot_batch)

    super_result = pd.concat(results)

    return super_result


def extract_types_from_csv(directory):
    all_types = set()

    # Traverse the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        print(files)
        for file in files:
            if file.endswith(".csv"):
                # Construct the full file path
                file_path = os.path.join(root, file)

                # Read the CSV file using pandas
                df = pd.read_csv(file_path)

                # Extract the "types" column and add unique values to the set
                types_column = df["types"]
                all_types.update(types_column.unique())

    return list(all_types)


def remove_file_from_paths(current_pat_idcode: str, project_name='new_project', verbosity=0) -> None:
    pat_file_paths = [
        f"{project_name}/current_pat_document_batches/",
        f"{project_name}/current_pat_document_batches_mct/",
        f"{project_name}/current_pat_documents_annotations_batches/",
        f"{project_name}/current_pat_documents_annotations_batches_mct/",
        f"{project_name}/current_pat_bloods_batches/",
        f"{project_name}/current_pat_drugs_batches/",
        f"{project_name}/current_pat_diagnostics_batches/",
        f"{project_name}/current_pat_news_batches/",
        f"{project_name}/current_pat_obs_batches/",
        f"{project_name}/current_pat_bmi_batches/",
        f"{project_name}/current_pat_demo_batches/"
    ]

    for path in pat_file_paths:
        file_path = path + current_pat_idcode + ".csv"
        try:
            os.remove(file_path)
            if verbosity > 0:
                print(f"{file_path} successfully removed")
        except FileNotFoundError:
            if verbosity > 0:
                print(f"{file_path} not found")
        except Exception as e:
            if verbosity > 0:
                print(f"Error removing {file_path}: {e}")


def process_chunk(args):
    part_chunk, all_files, part_size, unique_columns = args
    concatenated_data = {column: [] for column in unique_columns}
    for file in all_files[part_chunk:part_chunk + part_size]:
        if file.endswith('.csv'):
            with open(file, 'r', newline='') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    for column in unique_columns:
                        concatenated_data[column].append(row.get(column, ''))
    return concatenated_data


def process_csv_files_multi(input_path, out_folder='outputs', output_filename_suffix='concatenated_output', part_size=336, sample_size=None, append_timestamp_column=False, n_proc=None):
    curate_columns = False

    all_file_paths = [os.path.join(dp, f) for dp, dn, filenames in os.walk(
        input_path) for f in filenames if os.path.splitext(f)[1] == '.csv']

    if type(sample_size) == str or sample_size is None:
        if sample_size is None or sample_size.lower() == 'all':
            sample_size = len(all_file_paths)

    output_file = os.path.join(
        out_folder, f'concatenated_data_{output_filename_suffix}.csv')

    unique_columns = set()

    all_files = all_file_paths if sample_size is None else all_file_paths[:sample_size]

    print("all files size", len(all_files))

    if not curate_columns:
        for file in tqdm(all_files):
            if file.endswith('.csv'):
                with open(file, 'r', newline='') as infile:
                    reader = csv.reader(infile)
                    try:
                        header = next(reader)
                        unique_columns.update(header)
                    except StopIteration:
                        pass

    if os.path.exists(output_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, extension = os.path.splitext(output_file)
        new_output_file = f"{base_name}_{timestamp}_overwritten{extension}"
        print(
            f"Warning: Output file already exists. Renaming {output_file} to {new_output_file}")
        os.rename(output_file, new_output_file)
    else:
        new_output_file = output_file

    unique_columns = list(unique_columns)
    unique_columns.sort(key=lambda x: x != 'client_idcode')

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=unique_columns)
        writer.writeheader()

    # Get the number of available CPU cores
    available_cores = cpu_count()

    # Set the desired number of processes (e.g., half of the available cores)
    desired_half_processes = available_cores // 2

    if (n_proc != None):
        if (n_proc == 'all'):
            n_proc_val = available_cores
        if (n_proc == 'half'):
            n_proc_val = desired_half_processes
        elif (type(n_proc) == int):
            n_proc_val = n_proc
    print("desried cores:", n_proc_val)

    with Pool(processes=n_proc_val) as pool:
        args_list = [(i, all_files, part_size, unique_columns)
                     for i in range(0, len(all_files), part_size)]
        results = list(tqdm(pool.imap(process_chunk, args_list),
                       total=len(all_files)//part_size))

    with open(output_file, 'a', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=unique_columns)
        for result in tqdm(results, desc='Writing lines...'):
            for i in range(len(result[next(iter(result))])):
                writer.writerow({column: result[column][i]
                                for column in unique_columns})

    if append_timestamp_column:
        print("Reading results and appending updatetime column")
        df = pd.read_csv(output_file)
        df = extract_datetime_to_column(df)
        df.to_csv(output_file)

    print(f"Concatenated data saved to {output_file}")

    return output_file


def join_icd10_codes_to_annot(df, inner=False):

    mfp = '/home/cogstack/samora/_data/gloabl_files/snomed_icd10_map/data/tls_Icd10cmHumanReadableMap_US1000124_20230901.tsv'

    mdf = pd.read_csv(mfp, sep='\t')

    if (inner == True):
        result = pd.merge(df, mdf, left_on='cui',
                          right_on='referencedComponentId', how='inner')

    else:
        result = pd.merge(df, mdf, left_on='cui',
                          right_on='referencedComponentId', how='left')

    return result


def join_icd10_OPC4S_codes_to_annot(df, inner=False):

    mfp = '/home/cogstack/samora/_data/gloabl_files/snomed_to_icd10_opcs4/map.csv'

    mdf = pd.read_csv(mfp)

    if (inner == True):
        result = pd.merge(df, mdf, left_on='cui',
                          right_on='conceptId', how='inner')

    else:
        result = pd.merge(df, mdf, left_on='cui',
                          right_on='conceptId', how='left')

    return result


def filter_and_select_rows(dataframe, filter_list, verbosity=0, time_column='updatetime', filter_column='cui', mode='earliest', n_rows=1):
    """
    Filter a dataframe based on a filter_column and filter_list, and return either the earliest or latest rows.

    Parameters:
    - dataframe (pd.DataFrame): Input dataframe.
    - filter_list (list): List of values to filter the dataframe.
    - verbosity (int): If True, print additional information during execution.
    - time_column (str): Column representing time, used for sorting if specified.
    - filter_column (str): Column used for filtering based on filter_list.
    - mode (str): Either 'earliest' or 'latest' to specify the rows to return.
    - n_rows (int): Number of rows to return if they exist.

    Returns:
    - pd.DataFrame: Filtered and selected rows from the input dataframe.
    """
    if not all(arg is not None for arg in [dataframe, filter_list, filter_column]):
        raise ValueError(
            "Please provide a valid dataframe, filter_list, and filter_column.")

    if filter_column not in dataframe.columns:
        raise ValueError(
            f"{filter_column} not found in the dataframe columns.")

    filtered_df = dataframe[dataframe[filter_column].isin(filter_list)]

    if time_column:
        filtered_df.sort_values(by=time_column, inplace=True)

    if mode == 'earliest':
        selected_rows = filtered_df.head(n_rows)
    elif mode == 'latest':
        selected_rows = filtered_df.tail(n_rows)
    else:
        raise ValueError("Invalid mode. Please choose 'earliest' or 'latest'.")

    if verbosity > 0:
        print("Filtered DataFrame:")
        print(filtered_df)
        print(f"Selected {mode} {n_rows} row(s):")
        print(selected_rows)

    return selected_rows


def filter_dataframe_by_cui(dataframe, filter_list, filter_column='cui', mode="earliest", temporal='before', verbosity=0, time_column='updatetime'):
    """
    Filter an annotation DataFrame based on a list of CUI codes and a specified mode.

    Parameters:
    - dataframe (pd.DataFrame): The input DataFrame.
    - filter_list (list): List of CUI codes to filter the DataFrame.
    - filter_column (str): The column containing filter. Default is 'cui'.
    - mode (str): Specifies whether to consider the earliest or latest entry for each filter. Default is "earliest".
    - temporal (str): Specifies whether to retain entries before or after the selected mode entry. Default is "before".
    - verbosity (int): Verbosity level. 0 for no debug statements, higher values for more verbosity.
    - time_column (str): The column containing time information. Default is 'updatetime'.

    Returns:
    - pd.DataFrame: Filtered DataFrame based on the specified criteria.
    """

    # Ensure the time column is in datetime format
    dataframe[time_column] = pd.to_datetime(dataframe[time_column], utc=True)

    # Ensure filter_list contains integers
    filter_list = [int(cui) for cui in filter_list]

    # Filter the DataFrame based on the given CUI codes
    filtered_df = dataframe[dataframe[filter_column].isin(filter_list)]

    # Debug statement for verbosity
    if verbosity > 0:
        print(f"Filtered DataFrame based on {filter_column} codes:\n")
        display(filtered_df.head())

    # Find the earliest or latest entry for each CUI code
    if mode == "earliest":
        result_df = filtered_df.groupby(filter_column, as_index=False)[
            time_column].min()
    elif mode == "latest":
        result_df = filtered_df.groupby(filter_column, as_index=False)[
            time_column].max()
    else:
        raise ValueError("Invalid mode. Use 'earliest' or 'latest'")

    filter_row = result_df.copy()  # preserve row used for filter
    # Debug statement for verbosity
    if verbosity > 0:
        print(f"Result DataFrame based on {mode} mode:\n")
        display(result_df.head())

    # Merge with the original DataFrame to get the full rows
    result_df = pd.merge(result_df, dataframe, on=[
                         filter_column, time_column], how='inner')

    # Filter the original DataFrame based on the earliest or latest entry
    if temporal == "before":
        filtered_original_df = dataframe[dataframe[time_column]
                                         <= result_df[time_column].min()]
    elif temporal == "after":
        filtered_original_df = dataframe[dataframe[time_column]
                                         >= result_df[time_column].max()]
    else:
        raise ValueError("Invalid temporal value. Use 'before' or 'after'")

    # Debug statement for verbosity
    if verbosity > 0:
        print(f"Filtered original DataFrame based on {temporal} temporal:\n")
        display(filtered_original_df.head())

    return filtered_original_df, filter_row, filtered_df


# Example usage:
# filter_codes = [109989006]
#
# Returns all rows after the earliest cui code match.
# filter_dataframe_by_cui(res, filter_list=filter_codes, filter_column = 'cui', mode="earliest", temporal = 'after', verbosity=3)


def copy_files_and_dirs(source_root: str, source_name: str, destination: str, items_to_copy: List[str] = None, loose_files: List[str] = None) -> None:
    """
    Useful for porting project files to a new project location.

    Copy specified directories and files from the source directory to the destination directory.

    Parameters:
        source_root (str): The root directory of the source project.
        source_name (str): The name of the source project directory.
        destination (str): The destination directory.
        items_to_copy (List[str], optional): List of directories/files to copy. Defaults to None.

    Returns:
        None

    Usage:
        project_root_source = "/home/cogstack/%USERNAME%/_data/HFE_5"
        project_name_source = "new_project"
        project_destination = "."

        copy_files_and_dirs(project_root_source, project_name_source, project_destination)
    """
    source_dir = os.path.join(source_root, source_name)

    # Create the destination directory if it doesn't exist
    destination_dir = os.path.join(destination, source_name)
    os.makedirs(destination_dir, exist_ok=True)

    if items_to_copy is None:
        # List of directories/files to copy
        items_to_copy = ['current_pat_annots_parts',
                         'current_pat_annots_mrc_parts',
                         'outputs',
                         'current_pat_document_batches',
                         'current_pat_document_batches_mct',
                         'current_pat_documents_annotations_batches',
                         'current_pat_documents_annotations_batches_mct',
                         'current_pat_lines_parts']

    # Get all paths from the source directory
    all_source_paths = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            all_source_paths.append(os.path.relpath(
                os.path.join(root, file), source_dir))
        for dir in dirs:
            all_source_paths.append(os.path.relpath(
                os.path.join(root, dir), source_dir))

    # Filter paths based on items_to_copy
    paths_to_copy = [path for path in all_source_paths if any(
        item in path for item in items_to_copy)]

    # Copy each path to the destination preserving structure
    for path in tqdm(paths_to_copy, desc="Copying"):
        source_path = os.path.join(source_dir, path)
        destination_path = os.path.join(destination_dir, path)

        if os.path.isdir(source_path):
            os.makedirs(destination_path, exist_ok=True)
        else:
            shutil.copy2(source_path, destination_path)

    if loose_files is None:
        # Look for loose files specifically in the root directory of the source
        loose_files = ['treatment_docs.csv', 'control_path.pkl']

    # Copy loose files to the root directory of the destination
    for loose_file in tqdm(loose_files, desc="Copying loose files"):
        source_loose_path = os.path.join(source_root, loose_file)
        destination_loose_path = os.path.join(destination, loose_file)
        shutil.copy2(source_loose_path, destination_loose_path)

    # Example usage:
    # if __name__ == "__main__":
    # project_root_source = "/home/cogstack/%USERNAME%/_data/HFE_5"
    # project_name_source = "new_project"
    # project_destination = "."

    # copy_files_and_dirs(project_root_source, project_name_source, project_destination)


def get_pat_ipw_record(
    current_pat_idcode: str,
    config_obj=None,
    annot_filter_arguments: Optional[Dict[str,
                                          Union[int, str, List[str]]]] = None,
    filter_codes: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Retrieve patient IPW record.

    Parameters:
    - current_pat_idcode (str): Patient ID code.
    - config_obj (Optional[pat2vec config obj]): Configuration object (default: None).
    - annot_filter_arguments (Optional[YourFilterArgType]): Annotation filter arguments (default: None).
    - filter_codes (Optional[int]): Filter codes (default: None).

    Returns:
    pd.DataFrame: DataFrame containing the earliest relevant records.
    """

    pre_document_annotation_batch_path = config_obj.pre_document_annotation_batch_path
    pre_document_annotation_batch_path_mct = config_obj.pre_document_annotation_batch_path_mct

    fsr = pd.DataFrame()
    fsr_mct = pd.DataFrame()

    # EPR annotations
    dfa = pd.read_csv(
        f'{pre_document_annotation_batch_path}/{current_pat_idcode}.csv')
    necessary_columns = ['client_idcode', 'updatetime', 'pretty_name', 'cui', 'type_ids', 'types', 'source_value',
                         'detected_name', 'acc', 'id', 'Time_Value', 'Time_Confidence', 'Presence_Value',
                         'Presence_Confidence', 'Subject_Value', 'Subject_Confidence']

    dfa = dfa.dropna(subset=necessary_columns)

    if annot_filter_arguments is not None:
        dfa = filter_annot_dataframe2(dfa, annot_filter_arguments)

    if len(dfa) > 0:
        fsr = filter_and_select_rows(dfa, filter_codes, verbosity=0, time_column='updatetime', filter_column='cui',
                                     mode='earliest', n_rows=1)

    # MCT annotations
    dfa_mct = pd.read_csv(
        f'{pre_document_annotation_batch_path_mct}/{current_pat_idcode}.csv')
    necessary_columns_mct = ['client_idcode', 'observationdocument_recordeddtm', 'pretty_name', 'cui', 'type_ids',
                             'types', 'source_value', 'detected_name', 'acc', 'id', 'Time_Value', 'Time_Confidence',
                             'Presence_Value', 'Presence_Confidence', 'Subject_Value', 'Subject_Confidence']

    dfa_mct = dfa_mct.dropna(subset=necessary_columns_mct)

    if annot_filter_arguments is not None:
        dfa_mct = filter_annot_dataframe2(dfa_mct, annot_filter_arguments)

    if len(dfa_mct) > 0:
        fsr_mct = filter_and_select_rows(dfa_mct, filter_codes, verbosity=0,
                                         time_column='observationdocument_recordeddtm', filter_column='cui',
                                         mode='earliest', n_rows=1)

    if not fsr.empty and not fsr_mct.empty:
        earliest_df = fsr if fsr['updatetime'].min(
        ) < fsr_mct['observationdocument_recordeddtm'].min() else fsr_mct
    elif not fsr.empty:
        earliest_df = fsr
    elif not fsr_mct.empty:
        earliest_df = fsr_mct
    else:
        # Both DataFrames are empty
        earliest_df = pd.DataFrame(columns=necessary_columns)
        earliest_df['client_idcode'] = [current_pat_idcode]

    earliest_df = earliest_df.copy()

    if len(earliest_df) == 0:
        display(earliest_df)

    return earliest_df


def filter_and_update_csv(target_directory, ipw_dataframe, filter_type='after', verbosity=False):
    for _, row in ipw_dataframe.iterrows():
        client_idcode = row['client_idcode']
        # print(client_idcode, row['updatetime'])
        # filter_date = pd.to_datetime(row['updatetime']).tz_convert('UTC')  # Convert filter_date to UTC
        filter_date = pd.to_datetime(
            row['updatetime'], utc=True, errors='coerce')

        if verbosity:
            print(f"Processing client_idcode: {client_idcode}")

        # Recursively walk through the target directory
        for root, dirs, files in os.walk(target_directory):
            for file in files:
                if file.startswith(client_idcode) and file.endswith('.csv'):
                    file_path = os.path.join(root, file)

                    if verbosity:
                        print(f"Found CSV file: {file_path}")

                    df = pd.read_csv(file_path)

                    # Check if 'updatetime' is in columns
                    if 'updatetime' in df.columns:
                        df['updatetime'] = pd.to_datetime(
                            df['updatetime'], utc=True, errors='coerce')
                        update_column = 'updatetime'
                    elif 'observationdocument_recordeddtm' in df.columns:
                        df['observationdocument_recordeddtm'] = pd.to_datetime(
                            df['observationdocument_recordeddtm'], utc=True, errors='coerce')
                        update_column = 'observationdocument_recordeddtm'
                    elif 'order_entered' in df.columns:
                        df['order_entered'] = pd.to_datetime(
                            df['order_entered'], utc=True, errors='coerce')
                        update_column = 'order_entered'
                    elif 'basicobs_entered' in df.columns:
                        df['basicobs_entered'] = pd.to_datetime(
                            df['basicobs_entered'], utc=True, errors='coerce')
                        update_column = 'basicobs_entered'
                    else:
                        print(
                            f"Warning: Neither 'updatetime', 'observationdocument_recordeddtm', 'order_entered', nor 'basicobs_entered' found in {file_path}")

                    # Drop rows with NaT values in the updated column
                    df = df.dropna(subset=[update_column])

                    if verbosity:
                        print(f"Updating CSV file based on {update_column}")

                    df[update_column] = pd.to_datetime(
                        df[update_column], utc=True)
                    filter_condition = df[update_column] > filter_date if filter_type == 'after' else df[update_column] < filter_date
                    filtered_df = df[filter_condition]
                    filtered_df.to_csv(file_path, index=False)

                    if verbosity:
                        print("CSV file updated successfully")


def build_ipw_dataframe(annot_filter_arguments=None, filter_codes=None, config_obj=None):

    df = pd.DataFrame()

    pat_list = os.listdir(config_obj.pre_document_batch_path)

    pat_list_stripped = [os.path.splitext(
        file)[0] for file in pat_list if file.endswith(".csv")]

    for pat in pat_list_stripped:

        res = get_pat_ipw_record(current_pat_idcode=pat, annot_filter_arguments=None,
                                 filter_codes=filter_codes, config_obj=config_obj)
        df = pd.concat([df, res], ignore_index=True)

    return df


def retrieve_pat_annots_mct_epr(client_idcode, config_obj, columns_epr=None, columns_mct=None, merge_time_columns=True):
    pre_document_annotation_batch_path = config_obj.pre_document_annotation_batch_path
    pre_document_annotation_batch_path_mct = config_obj.pre_document_annotation_batch_path_mct

    dfa = pd.read_csv(
        f'{pre_document_annotation_batch_path}/{client_idcode}.csv', usecols=columns_epr)

    dfa_mct = pd.read_csv(
        f'{pre_document_annotation_batch_path_mct}/{client_idcode}.csv', usecols=columns_mct)

    all_annots = pd.concat([dfa, dfa_mct], ignore_index=True)

    if merge_time_columns:
        all_annots['updatetime'] = all_annots['updatetime'].fillna(
            all_annots['observationdocument_recordeddtm'])
        all_annots['observationdocument_recordeddtm'] = all_annots['observationdocument_recordeddtm'].fillna(
            all_annots['updatetime'])

    return all_annots


def check_list_presence(df, column, lst, annot_filter_arguments=None):

    if annot_filter_arguments is not None:
        df = filter_annot_dataframe2(df, annot_filter_arguments)

    str_lst = list(map(str, lst))  # Convert elements to strings
    return any(df[column].astype(str).str.contains('|'.join(str_lst), case=False, na=False))


# Check if at least one element from each list is present in the 'cui' column
# result = all(check_list_presence(all_annots, 'cui', lst) for lst in n_lists)
