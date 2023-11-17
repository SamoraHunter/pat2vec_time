

from os.path import exists
import pandas as pd
import numpy as np
import csv
from csv import writer
import warnings
import multiprocessing
from multiprocessing import Pool
#import tqdm
import re
import sys  
import numpy as np
import os, sys
from IPython.utils import io

#from tqdm import trange
from colorama import Fore, Back, Style
color_bars = [Fore.RED,
    Fore.GREEN,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.YELLOW,
    Fore.CYAN,
    Fore.WHITE]

import os
from pathlib import Path
import paramiko
from os.path import exists
import random
from datetime import datetime, timedelta, timezone
#nb_full_path = os.path.join(os.getcwd(), nb_name)
import datetime as dt
import logging

from medcat.cat import CAT

import config_pat2vec

from cogstack_v8_lite import * # wrap with option and put behind boolean check, no wildcard in function. 
from credentials import *


#stuff paths for portability
sys.path.insert(0,'/home/aliencat/samora/gloabl_files')
sys.path.insert(0,'/data/AS/Samora/gloabl_files')
sys.path.insert(0,'/home/jovyan/work/gloabl_files')
sys.path.insert(0, '/home/cogstack/samora/_data/gloabl_files')


from pathlib import Path

from COGStats import *
from scipy import stats
import pickle


import traceback
from datetime import datetime
def convert_date(date_string):
    date_string = date_string.split("T")[0]
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    return date_object

import os
import subprocess
from io import StringIO

from datetime import datetime
from dateutil.relativedelta import relativedelta




class main:
    def __init__(self, parameter1, parameter2, aliencat=False, dgx=False, dhcap=False, dhcap02=True,
             batch_mode=True, remote_dump=False, negated_presence_annotations=False,
             store_annot=True, share_sftp=True, multi_process=True, annot_first=False,
             strip_list=True, cogstack=True, verbosity = 0, config = None, use_filter=False,
             json_filter_path = None, random_seed_val=42, treatment_client_id_list = None,
             hostname =None):


        # Additional parameters
        self.aliencat = aliencat
        self.dgx = dgx
        self.dhcap = dhcap
        self.dhcap02 = dhcap02
        self.batch_mode = batch_mode
        self.remote_dump = remote_dump
        self.negated_presence_annotations = negated_presence_annotations
        self.store_annot = store_annot
        self.share_sftp = share_sftp
        self.multi_process = multi_process
        self.annot_first = annot_first
        self.strip_list = strip_list
        self.verbosity = verbosity
        self.random_seed_val = random_seed_val
        self.treatment_client_id_list = treatment_client_id_list
        self.hostname = hostname
        
        if(config==None):
            config = config_pat2vec.config_class()
            
        
        
    
        #config parameters
        self.suffix = config.suffix
        self.treatment_doc_filename = config.treatment_doc_filename
        self.treatment_control_ratio_n = config.treatment_control_ratio_n
        self.pre_annotation_path = config.pre_annotation_path
        self.pre_annotation_path_mrc = config.pre_annotation_path_mrc
        self.proj_name = config.proj_name

        

        
        # Create a folder for logs if it doesn't exist
        log_folder = "logs"
        os.makedirs(log_folder, exist_ok=True)

        # Create a logger
        self.logger = logging.getLogger(__name__)

        # Create a handler that writes log messages to a file with a timestamp
        log_file = f"{log_folder}/logfile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)

        # Create a formatter to include timestamp in the log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Optionally set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        self.logger.setLevel(logging.DEBUG)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)

        # Optionally, add a StreamHandler to print log messages to the console as well
        stdout_handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(stdout_handler)

        # Now you can use the logger to log messages within the class
        self.logger.info("Initialized pat2vec.main")
        


        
        
        if self.verbosity > 0:
            print(self.pre_annotation_path)
            print(self.pre_annotation_path_mrc)
            
            
        self.use_filter = use_filter
        
        if(self.use_filter):
            self.json_filter_path = json_filter_path
            import json

            with open(self.json_filter_path, 'r') as f:
                json_data = json.load(f)
                
            len(json_data['projects'][0])
            json_cuis = json_data['projects'][0]['cuis'].split(",")
            self.cat.cdb.filter_by_cui(json_cuis)
    
        if not(self.dhcap) and not (self.dhcap02):

            gpu_index,free_mem  = self.get_free_gpu()

        if(int(free_mem)>4000):
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_index)
            print(f"Setting gpu with {free_mem} free")
        else:
            print(f"Setting NO gpu, most free memory: {free_mem} !")
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"



    
    


        random.seed(self.random_seed_val)
        use_controls = False
        if(use_controls):
            # Get control docs default 1:1

            all_idcodes = pd.read_csv('all_client_idcodes_epr_unique.csv')['client_idcode']

            
            print(len(all_idcodes), len(self.treatment_client_id_list))

            full_control_client_id_list = list(set(all_idcodes) - set(self.treatment_client_id_list))
            
            full_control_client_id_list.sort() # ensure sort for repeatability

            len(full_control_client_id_list) - len(all_idcodes)

            n_treatments = len(self.treatment_client_id_list) * self.treatment_control_ratio_n
            print(f"{n_treatments} selected as controls") #Soft control selection, many treatments will be false positives
            treatment_control_sample = pd.Series(full_control_client_id_list).sample(n_treatments, random_state=42)

            treatment_control_sample

            self.all_patient_list_control = list(treatment_control_sample.values)
            
            with open('control_list.pkl', 'wb') as f:
                pickle.dump(self.all_patient_list_control, f)
                
            print(self.all_patient_list_control[0:10])
            
            

        self.all_patient_list = list(self.treatment_client_id_list)



        random.shuffle(self.all_patient_list)
        
        






        print(f"remote_dump {self.remote_dump}")
        print(self.pre_annotation_path)
        print(self.pre_annotation_path_mrc)
        print(self.current_pat_line_path)

        if(self.remote_dump):


            pre_path = f'/mnt/hdd1/samora/{self.proj_name}/'

    


    

    

        # Set the hostname, username, and password for the remote machine
        
        if(not self.aliencat or self.dgx):
            hostname = '%HOSTIPADDRESS%'
            
        if(self.aliencat and not self.dgx):
            hostname = 'localhost'
        
        username = '%USERNAME%'
        password = '%PASSWORD%'

        # Create an SSH client and connect to the remote machine
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, password=password)

        sftp_client = ssh_client.open_sftp()

        if(self.remote_dump):
            try:
                sftp_client.chdir(pre_path)  # Test if remote_path exists
            except IOError:
                sftp_client.mkdir(pre_path)  # Create remote_path



        pre_annotation_path = f"{pre_path}{self.pre_annotation_path}"
        pre_annotation_path_mrc = f"{pre_path}{self.pre_annotation_path_mrc}"
        current_pat_line_path = f"{pre_path}{self.current_pat_line_path}"
        current_pat_lines_path = current_pat_line_path
        
        
        if(self.remote_dump==False):
            Path(self.current_pat_annot_path).mkdir(parents=True, exist_ok=True)
            Path(pre_annotation_path_mrc).mkdir(parents=True, exist_ok=True)

        else:
            try:
                sftp_client.chdir(pre_annotation_path)  # Test if remote_path exists
            except IOError:
                sftp_client.mkdir(pre_annotation_path)  # Create remote_path

            try:
                sftp_client.chdir(pre_annotation_path_mrc)  # Test if remote_path exists
            except IOError:
                sftp_client.mkdir(pre_annotation_path_mrc)  # Create remote_path
                
            try:
                sftp_client.chdir(current_pat_line_path)  # Test if remote_path exists
            except IOError:
                sftp_client.mkdir(current_pat_line_path)  # Create remote_path
        else:
            sftp_client = None
            
            
            
            
            
            
            
    
    
            
            
            
    def sftp_exists(self, path, sftp_obj=None):
        try:
            if(self.share_sftp == False):
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname, username=username, password=password)

                sftp_obj = ssh_client.open_sftp()
            
            sftp_obj.stat(path)
            
            if(self.share_sftp == False):
                sftp_obj.close()
                sftp_obj.close()
            return True
        except FileNotFoundError:
            return False



    def generate_date_list(start_date, years, months, days):
    
        end_date = start_date + relativedelta(years=years, months=months, days=days)
        
        date_list = []
        current_date = start_date
        
        while current_date <= end_date:
            date_list.append((current_date.year, current_date.month, current_date.day))
            current_date += timedelta(days=1)
        
        return date_list






    def dump_results(self, file_data, path, sftp_obj=None):
        if(self.remote_dump):
            if(self.share_sftp == False):
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname, username=username, password=password)

                sftp_client = ssh_client.open_sftp()
                sftp_obj = sftp_client
            
            
            with sftp_obj.open(path, 'w') as file:
        
                pickle.dump(file_data, file)
            if(self.share_sftp == False):
                sftp_obj.close()
                sftp_obj.close()
            
        else:
            with open(path, 'wb') as f:
                pickle.dump(file_data, f)









    def list_dir_wrapper(self, path, sftp_obj=None):
        #global sftp_client
        if(self.remote_dump):
            if(self.share_sftp == False):
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname, username=username, password=password)

                sftp_client = ssh_client.open_sftp()
                sftp_obj = sftp_client
            elif(sftp_obj ==None):
                sftp_obj = sftp_client
                
            res = sftp_obj.listdir(path)
            
            
            return res
            
        else:
            
            return os.listdir(path)





    def exist_check(self, path, sftp_obj=None):
        if(self.remote_dump):
            return self.sftp_exists(path, sftp_obj)
        else:
            return exists(path)


    def get_free_gpu():
        ## move to cogstats?
        gpu_stats = subprocess.check_output(["nvidia-smi", "--format=csv", "--query-gpu=memory.used,memory.free"])
        gpu_df = pd.read_csv(StringIO(gpu_stats.decode('utf-8')),
                            names=['memory.used', 'memory.free'],
                            skiprows=1)
        print('GPU usage:\n{}'.format(gpu_df))
        gpu_df['memory.free'] = gpu_df['memory.free'].map(lambda x: x.rstrip(' [MiB]'))
        idx = gpu_df['memory.free'].astype(int).idxmax()
        print('Returning GPU{} with {} free MiB'.format(idx, gpu_df.iloc[idx]['memory.free']))
        return int(idx), gpu_df.iloc[idx]['memory.free']







    def method1(self):
        
        self.logger.debug("This is a debug message from your_method.")
        self.logger.warning("This is a warning message from your_method.")

        # Code for method1
        pass

    def method2(self):
        # Code for method2
        pass

    def __str__(self):
        return f"MyClass instance with parameters: {self.parameter1}, {self.parameter2}"



    