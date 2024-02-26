from typing import Union
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import Optional
import pandas as pd
import json
import pandas as pd
import os
import textwrap
from tqdm import tqdm
from IPython.display import clear_output
from typing import List, Union


def medcat_trainer_export_to_df(file_path: str) -> pd.DataFrame:
    """
    Convert MedCATTrainer export JSON file to a pandas DataFrame.

    Parameters:
    - file_path (str): Path to the JSON file containing MedCATTrainer export data.

    Returns:
    - df (pd.DataFrame): DataFrame containing the extracted data.
    """
    # Load the JSON data
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Initialize lists to store extracted data
    annotations_data = []

    # Iterate through projects, documents, and annotations
    for project in data['projects']:
        project_name = project['name']
        project_id = project['id']

        for document in project['documents']:
            document_id = document['id']
            document_name = document['name']
            text = document['text']

            for annotation in document['annotations']:
                annotation_id = annotation['id']
                user = annotation['user']
                cui = annotation['cui']
                value = annotation['value']
                start = annotation['start']
                end = annotation['end']
                validated = annotation['validated']
                correct = annotation['correct']
                deleted = annotation['deleted']
                alternative = annotation['alternative']
                killed = annotation['killed']
                irrelevant = annotation['irrelevant']
                create_time = annotation['create_time']
                last_modified = annotation['last_modified']
                comment = annotation['comment']
                manually_created = annotation['manually_created']

                # Extract meta annotations
                meta_anns = annotation.get('meta_anns', {})
                subject_experiencer = meta_anns.get('Subject/Experiencer', {}).get('value')
                presence = meta_anns.get('Presence', {}).get('value')
                time = meta_anns.get('Time', {}).get('value')

                # Append extracted data to the list
                annotations_data.append({
                    'project_name': project_name,
                    'project_id': project_id,
                    'document_id': document_id,
                    'document_name': document_name,
                    'text': text,
                    'annotation_id': annotation_id,
                    'user': user,
                    'cui': cui,
                    'value': value,
                    'start': start,
                    'end': end,
                    'validated': validated,
                    'correct': correct,
                    'deleted': deleted,
                    'alternative': alternative,
                    'killed': killed,
                    'irrelevant': irrelevant,
                    'create_time': create_time,
                    'last_modified': last_modified,
                    'comment': comment,
                    'manually_created': manually_created,
                    'subject_experiencer': subject_experiencer,
                    'presence': presence,
                    'time': time
                })

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(annotations_data)
    return df

# Example usage:
# df = medcat_trainer_export_to_df('merge4.json')
# print(df)




def extract_labels_from_medcat_annotation_export(df: pd.DataFrame, human_labels: pd.DataFrame, window: int = 300, output_file: Union[str, None] = None) -> pd.DataFrame:
    """
    Extract labels from MedCAT annotation export.

    Parameters:
    - df (pd.DataFrame): The trainer output in DataFrame form Hint. medcat_trainer_export_to_df.
    - human_labels (pd.DataFrame): The DataFrame containing human labels.
    - window (int): The window size for extracting text samples. Default is 300.
    - output_file (str, optional): The file path to write the processed DataFrame. If not provided, the output will not be saved to a file.

    Returns:
    - pd.DataFrame: The processed human_labels DataFrame.
    """

    human_labels['extracted_label'] = np.nan

    for j in tqdm(range(0, len(df))):
        main_text = df.iloc[j]['text']
        main_value = df.iloc[j]['value']
        mapped_annot_doc_entity = main_text
        start = df.iloc[j]['start']
        end = df.iloc[j]['end']
        document_len = len(mapped_annot_doc_entity)
        virtual_start = max(0, start - window)
        virtual_end = min(document_len, end + window)
        main_text_sample = mapped_annot_doc_entity[virtual_start:virtual_end]

        for i in range(0, len(human_labels)):
            label_text = human_labels.iloc[i]['text_sample']
            label_value = human_labels.iloc[i]['source_value']

            if label_text in main_text:
                if main_text_sample == label_text:
                    if main_value == label_value:
                        extracted_bool = ((df.iloc[j]['subject_experiencer'] == 'Patient') &
                                          (df.iloc[j]['presence'] == 'True') &
                                          ((df.iloc[j]['time'] == 'Recent') | (df.iloc[j]['time'] == 'Past')))
                        human_labels.at[i, 'extracted_label'] = int(extracted_bool)

    if output_file is not None:
        human_labels.to_csv(output_file, index=False)

    return human_labels


def recreate_json(df: pd.DataFrame, output_file: Optional[str] = None) -> str:
    """
    Convert exported MedCAT trainer output DataFrame to JSON format suitable for training a MedCAT model.

    Args:
        df (pd.DataFrame): DataFrame containing exported data from MedCAT trainer.
        output_file (Optional[str]): Optional. File path to save the generated JSON. If not provided, JSON is not saved.

    Returns:
        str: JSON string representing the MedCAT training data.

    Example:
        # Assuming df contains the exported data
        output_filename = 'recreated_annotations.json'
        recreated_json = recreate_json(df, output_file=output_filename)
        print(recreated_json)
    """
    projects = []
    
    # Group by project and document
    grouped = df.groupby(['project_name', 'project_id', 'document_id', 'document_name', 'text'])
    
    for (project_name, project_id, document_id, document_name, text), group_data in grouped:
        documents = []
        
        for _, annotation_data in group_data.iterrows():
            annotation = {
                'id': annotation_data['annotation_id'],
                'user': annotation_data['user'],
                'cui': annotation_data['cui'],
                'value': annotation_data['value'],
                'start': annotation_data['start'],
                'end': annotation_data['end'],
                'validated': annotation_data['validated'],
                'correct': annotation_data['correct'],
                'deleted': annotation_data['deleted'],
                'alternative': annotation_data['alternative'],
                'killed': annotation_data['killed'],
                'irrelevant': annotation_data['irrelevant'],
                'create_time': annotation_data['create_time'],
                'last_modified': annotation_data['last_modified'],
                'comment': annotation_data['comment'],
                'manually_created': annotation_data['manually_created'],
                'meta_anns': {
                    'Subject/Experiencer': {'value': annotation_data['subject_experiencer']},
                    'Presence': {'value': annotation_data['presence']},
                    'Time': {'value': annotation_data['time']}
                }
            }
            documents.append(annotation)
        
        project = {
            'name': project_name,
            'id': int(project_id),
            'documents': [
                {
                    'id': int(document_id),
                    'name': document_name,
                    'text': text,
                    'annotations': documents,
                    'relations': []
                }
            ]
        }
        projects.append(project)
    
    reconstructed_json = {'projects': projects}
    json_str = json.dumps(reconstructed_json, indent=4)
    
    # Optionally write to file if output_file is provided
    if output_file:
        with open(output_file, 'w') as f:
            f.write(json_str)
    
    return json_str

# Example usage:
# # Call the function with your DataFrame and output filename
# output_filename = 'recreated_annotations.json'
# recreated_json = recreate_json(df, output_file=output_filename)

# # Print the recreated JSON
# print(recreated_json)

def manually_label_annotation_df(df: pd.DataFrame, file_path: str = 'human_labels.csv', confirmatory: bool = False, verbose: bool = False, filter_codes_list: List[List[str]] = []) -> None:
    """
    Loop over an annotation DataFrame and display annotations for unique client idcodes until they have a confirmed by user correct annotation.
    The human labeling is stored in the file_path supplied.

    Args:
        df (pd.DataFrame): The DataFrame to annotate.
        file_path (str, optional): The file path to store human labels. Defaults to 'human_labels.csv'.
        confirmatory (bool, optional): Whether to perform confirmatory annotations. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        filter_codes_list (List[List[str]], optional): A list of lists of filter codes. Defaults to [].

    Returns:
        None
    """
    counter = 0
    if os.path.exists(file_path):
        if verbose:
            print("Reading human labels from file...")
        human_labels = pd.read_csv(file_path)
    else:
        if verbose:
            print("Creating new human labels DataFrame...")
        human_labels = pd.DataFrame(columns=['human_label'])
    
    if 'human_label' not in df.columns:
        df['human_label'] = human_labels['human_label']
    
    for index, row in tqdm(df.iterrows()):
        if confirmatory:
            if pd.notnull(row['client_idcode']):
                existing_labels = [df[(df['client_idcode'] == row['client_idcode']) & (df['human_label'] == 1) & (df['cui'].isin(filter_codes))] for filter_codes in filter_codes_list]

                if not all(label.empty for label in existing_labels):
                    continue  # Skip rows if there is at least one label from each of the supplied lists
        
        if pd.isnull(row['human_label']):
            remaining_labels_info = [(len(df[(df['client_idcode'] == row['client_idcode']) & (df['human_label'] != 1) & (df['cui'].isin(filter_codes))]),
                                      len(df[(df['client_idcode'] == row['client_idcode']) & (df['cui'].isin(filter_codes))])) for filter_codes in filter_codes_list]
            
            if verbose:
                print("Printing text sample for user input...")
            text_sample = row['text_sample']
            source_value = row['source_value']
            highlighted_text = text_sample.replace(source_value, f"\033[1m{source_value}\033[0m") # Bold highlight
            highlighted_text = text_sample.replace(source_value, f"\033[4;1m{source_value}\033[0m") # Underline and bold highlight

            # Wrap the text to fit within standard scroll window width
            wrapped_text = textwrap.fill(highlighted_text, width=80)
            print(wrapped_text)

            clear_output(wait=True) # Clear Jupyter notebook display
            label = input(f"Labelling {row['client_idcode']} Press enter for 1 or enter 0 for 0.: ")
            if label == '':
                label = 1
            elif label == 'quit' or label== 'end':
                raise ValueError("User ended the labeling process.")
            elif label != '':
                label = 0
            
            df.at[index, 'human_label'] = label
            
            if counter % 10 == 0:
                df.to_csv(file_path, index=False)  # Write to file immediately
                print('saved df!')
            counter += 1
            
            print(df[df['human_label'].isna()].shape[0], df[df['human_label'].notna()].shape[0])
            print(df[df['human_label'].isna()]['client_idcode'].unique().shape, df[df['human_label'].notna()]['client_idcode'].unique().shape)
            for i, filter_codes in enumerate(filter_codes_list):
                print(f"Remaining labels for filter {i + 1} as a total of codes: {remaining_labels_info[i][0]}/{remaining_labels_info[i][1]}")
    
    if verbose:
        print("Writing human labels to file...")
    
    df.to_csv(file_path, index=False)
    print('saved df!')
    counter += 1

# Example usage:
# Assuming df is your DataFrame with the columns 'text_sample', 'source_value', and 'client_idcode'
# And filter_codes_list is a list of lists of filter codes
#annotate_dataframe(output_csv_file_sorted, confirmatory=True, verbose=True, filter_codes_list=[hfe_filter_codes_float, phleb_filter_codes_float])
