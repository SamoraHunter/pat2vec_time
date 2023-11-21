from datetime import datetime
from pathlib import Path

import pandas as pd


class config_class:
    def __init__(self,
                 remote_dump=False,
                 suffix='',
                 treatment_doc_filename='treatment_docs.csv',
                 treatment_control_ratio_n=1,
                 proj_name='new_project',
                 current_path_dir=".",
                 main_options = None,
                 start_date = (datetime(1995, 1, 1)),
                 years = 0,
                 months = 0, 
                 days = 1,
                 ):
        
        
        self.suffix = suffix
        self.treatment_doc_filename = treatment_doc_filename
        self.treatment_control_ratio_n = treatment_control_ratio_n
        self.pre_annotation_path = f'current_pat_annots_parts{self.suffix}/'
        self.pre_annotation_path_mrc = f'current_pat_annots_mrc_parts{self.suffix}/'
        
        self.proj_name = proj_name
        self.main_options = main_options

        
        if(self.main_options == None):
            self.main_options = {'demo':False,
                'bmi':False,
                'bloods':False,
                'drugs':False,
                'diagnostics':False,
                
                'core_02':False,
                'bed':False,
                'vte_status':False,
                'hosp_site':False,
                'core_resus':False,
                'news':False,
                
                'annotations':True,
                'annotations_mrc': True,
                
               }



        if(remote_dump==False):
        
            # pre_path = f'/mnt/hdd1/samora/{proj_name}/'
            # pre_path = f'/home/jovyan/work/clinical_coding/{proj_name}/'
            # pre_path = f'/home/cogstack/samora/_data/clinical_coding/{proj_name}/'
            pre_path = f'{current_path_dir}{proj_name}/'
            
            pre_annotation_path = pre_path + pre_annotation_path
            
            pre_annotation_path_mrc = pre_path + pre_annotation_path_mrc
            
            Path(pre_annotation_path).mkdir(parents=True, exist_ok=True)
            Path(pre_annotation_path_mrc).mkdir(parents=True, exist_ok=True)

            print(pre_annotation_path)
            print(pre_annotation_path_mrc)
            
            
        self.current_pat_line_path = f"current_pat_lines_parts{suffix}/"

        if(remote_dump==False):
            
            self.current_pat_line_path = pre_path + self.current_pat_line_path
            
            self.current_pat_lines_path = self.current_pat_line_path
            
            Path(self.current_pat_line_path).mkdir(parents=True, exist_ok=True)
        


        print(self.current_pat_line_path)
        
        
        self.start_date = start_date
        self.years = years
        self.months = months
        self.days = days
        
        
        
        
        
        months = [x for x in range(1,4)]
        years = [x for x in range(2023, 2024)]
        days = [x for x in range(1,32)]
        import itertools
        combinations = list(itertools.product(years, months, days))
        len(combinations)
        
        
        
        self.slow_execution_threshold_low  = 10
        self.slow_execution_threshold_high = 30
        self.slow_execution_threshold_extreme = 60
        
        
        
        
        priority_list_bool = False

        if(priority_list_bool):
            #add logic to prioritise pats from list.
            
            df_old_done = pd.read_csv('/data/AS/Samora/HFE/HFE/v18/current_pat_lines_parts/current_pat_lines__part_0_merged.csv',usecols=['client_idcode', 'Hemochromatosis (disorder)_count_subject_present'])
            
            priority_list = df_old_done[df_old_done['Hemochromatosis (disorder)_count_subject_present']>0]['client_idcode'].to_list()
            
            all_patient_list = priority_list #+ all_patient_list
            
        