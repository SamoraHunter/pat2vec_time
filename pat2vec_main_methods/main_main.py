import time
import traceback

import pandas as pd

from util.methods_get import (enum_target_date_vector, list_dir_wrapper,
                              update_pbar, write_remote)


def main(current_pat_client_id_code, target_date_range, config_obj = None, main_options = None ):
        #global skipped_counter
        #global start_time
        
        skipped_counter = config_obj.skipped_counter
        start_time = config_obj.start_time
        stripped_list_start = config_obj.stripped_list_start
        current_pat_lines_path = config_obj.current_pat_lines_path
        stfp_obj = config_obj.sftp_obj
        sftp_client = config_obj.sftp_client
        
        current_pat_line_path = config_obj.current_pat_line_path
        
        remote_dump = config_obj.remote_dump
        
        multi_process = config_obj.multi_process
        
        start_time = time.time()
        
        
        
        
        
        done_list = []
        if(current_pat_client_id_code+"_"+str(target_date_range) not in stripped_list_start):
            
            
            stripped_list = [x.replace(".csv","") for x in list_dir_wrapper(current_pat_lines_path)]

            if(current_pat_client_id_code + "_" + str(target_date_range) not in stripped_list):
                #print(start_time, current_pat_client_id_code)
                try:
                    #current_pat_client_id_code = all_patient_list[k]

                    patient_vector = []
                    
                    p_bar_entry = current_pat_client_id_code + "_" + str(target_date_range)
                    #

                    update_pbar(p_bar_entry, start_time, 0, 'demo')

                    
                    if(main_options.get('demo')):
                        current_pat_demo = get_demo(current_pat_client_id_code, target_date_range)
                        patient_vector.append(current_pat_demo)


                    update_pbar(p_bar_entry, start_time, 1, 'bmi')

                    if(main_options.get('bmi')):
                        bmi_features = get_bmi_features(current_pat_client_id_code, target_date_range)
                        patient_vector.append(bmi_features)


                    update_pbar(p_bar_entry, start_time, 2, 'bloods')

                    if(main_options.get('bloods')):
                        current_pat_bloods = get_current_pat_bloods(current_pat_client_id_code, target_date_range)
                        patient_vector.append(current_pat_bloods)

                    update_pbar(p_bar_entry, start_time, 3, 'drugs')

                    if(main_options.get('drugs')):
                        current_pat_drugs = get_current_pat_drugs(current_pat_client_id_code, target_date_range)
                        patient_vector.append(current_pat_drugs)

                    update_pbar(p_bar_entry, start_time, 4, 'diagnostics')

                    if(main_options.get('diagnostics')):
                        current_pat_diagnostics = get_current_pat_diagnostics(current_pat_client_id_code, target_date_range)
                        patient_vector.append(current_pat_diagnostics)

                    #update_pbar(current_pat_client_id_code, start_time, 5, 'annotations', n_docs_to_annotate)


                    if(main_options.get('annotations')):
                        df_pat_target = get_current_pat_annotations(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    if(main_options.get('annotations_mrc')):
                        df_pat_target = get_current_pat_annotations_mrc_cs(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                    
                    update_pbar(p_bar_entry, start_time, 1, 'core_02')
                    
                    if(main_options.get('core_02')):
                        df_pat_target = get_core_02(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 2, 'bed')
                        
                    if(main_options.get('bed')):
                        df_pat_target = get_bed(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 3, 'vte_status')
                        
                    if(main_options.get('vte_status')):
                        df_pat_target = get_vte_status(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 4, 'hosp_site')    
                        
                    if(main_options.get('hosp_site')):
                        df_pat_target = get_hosp_site(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 1, 'core_resus')     
                        
                    if(main_options.get('core_resus')):
                        df_pat_target = get_core_resus(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 2, 'news')      
                        
                    if(main_options.get('news')):
                        df_pat_target = get_news(current_pat_client_id_code, target_date_range)
                        patient_vector.append(df_pat_target)
                        
                    update_pbar(p_bar_entry, start_time, 2, 'concatenating')
                    
                    target_date_vector = enum_target_date_vector(target_date_range, current_pat_client_id_code)
                    
                        
                    patient_vector.append(target_date_vector)
                    

                    pat_concatted = pd.concat(patient_vector, axis=1)

                    pat_concatted.drop('client_idcode', axis=1, inplace=True)

                    pat_concatted.insert(0, 'client_idcode', current_pat_client_id_code)
                    
                    update_pbar(p_bar_entry, start_time, 2, 'saving...')
                    
                    output_path = current_pat_line_path  + current_pat_client_id_code + "/" +str(current_pat_client_id_code) + "_" + str(target_date_range)+".csv"
                    
                    
                    if(remote_dump==False):
                    
                        pat_concatted.to_csv(output_path)   
                    else:
                        
                        if(multi_process == True):
                            
                            write_remote(output_path, pat_concatted, stfp_obj)
                        else:
                            with sftp_client.open(output_path, 'w') as file:
                                pat_concatted.to_csv(file)
                    
                    update_pbar(p_bar_entry, start_time, 2, f'Done {len(pat_concatted.columns)} cols in {int(time.time() - start_time)}s, {int(len(pat_concatted.columns)/int(time.time() - start_time))} p/s')
                    
                    #print(time.time() - start_time, current_pat_client_id_code)
                except RuntimeError as RuntimeError_exception:
                    print("Caught runtime error... is torch?")
                    print(RuntimeError)
                    print("sleeping 1h")
                    time.sleep(3600)

                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    print(f"Reproduce on {current_pat_client_id_code, target_date_range}")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(e).__name__, e.args)
                    print(message)
        
            else:
                skipped_counter = skipped_counter + 1
                pass
                #print(f"{current_pat_client_id_code} done already")
                #pat_concatted
                