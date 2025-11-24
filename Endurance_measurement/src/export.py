
import os
import pandas as pd
import csv


def main_export_csv(Dataframe_DHM, Dataframe_CVM, Dataframe_PUND, metadata_dict_DHM, metadata_dict_CVM, metadata_dict_PUND, output_path, base_name):

    # We store the csv in the csv folder in the main result folder
    output_csv_data_path = os.path.join(output_path, "CSV_data")
    os.makedirs(output_csv_data_path, exist_ok=True)  # Ensure output directory exists

    if metadata_dict_DHM["DHM_present"] == True:

        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_DHM["Measurement_date_iso"]}_{base_name}_Main-DHM.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_DHM.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe_DHM.to_csv(csv_filename, index=False, sep='\t', mode='a')


    if metadata_dict_CVM["CVM_present"] == True:

        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_CVM["Measurement_date_iso"]}_{base_name}_Main-CVM.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_CVM.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe_CVM.to_csv(csv_filename, index=False, sep='\t', mode='a') 


    if metadata_dict_PUND["PUND_present"] == True:

        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_PUND["Measurement_date_iso"]}_{base_name}_Main-PUND.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_PUND.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe_PUND.to_csv(csv_filename, index=False, sep='\t', mode='a') 





# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def export_csv_DHM(Dataframe, metadata_dict_DHM, output_path, base_name):
    if metadata_dict_DHM["DHM_present"] == True:
        # We store the csv in the csv folder in the main result folder
        output_csv_data_path = os.path.join(output_path, "CSV_data")
        os.makedirs(output_csv_data_path, exist_ok=True)  # Ensure output directory exists


        Dataframe = pd.concat(Dataframe, axis = 1)    # Concatenate all dataframes along columns
        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_DHM["Measurement_date_iso"]}_{base_name}_FatigueDHM.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_DHM.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "DHM_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe.to_csv(csv_filename, index=False, sep='\t', mode='a')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def export_csv_CVM(Dataframe, metadata_dict_CVM, output_path, base_name):
    if metadata_dict_CVM["CVM_present"] == True:
        # We store the csv in the csv folder in the main result folder
        output_csv_data_path = os.path.join(output_path, "CSV_data")
        os.makedirs(output_csv_data_path, exist_ok=True)  # Ensure output directory exists


        Dataframe = pd.concat(Dataframe, axis = 1)    # Concatenate all dataframes along columns
        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_CVM["Measurement_date_iso"]}_{base_name}_FatigueCVM.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_CVM.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "CVM_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe.to_csv(csv_filename, index=False, sep='\t', mode='a')   

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                         

def export_csv_PUND(Dataframe, metadata_dict_PUND, output_path, base_name):
    if metadata_dict_PUND["PUND_present"] == True:
        # We store the csv in the csv folder in the main result folder
        output_csv_data_path = os.path.join(output_path, "CSV_data")
        os.makedirs(output_csv_data_path, exist_ok=True)  # Ensure output directory exists


        Dataframe = pd.concat(Dataframe, axis = 1)    # Concatenate all dataframes along columns
        csv_filename = os.path.join(output_csv_data_path, f"{metadata_dict_PUND["Measurement_date_iso"]}_{base_name}_FatiguePUND.csv")
        
        # We store the string values of the metadata dictionary into a list and we replace ":" by tab
        values_list = []
        for key,value in metadata_dict_PUND.items():  # Use .values() to get only the values
            value_tab = None
            if key == "Measurement_date_raw":
                continue  # Skip this key-value pair
            if key == "Measurement_date_iso":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_present":
                continue  # Skip this key-value pair
            elif key == "Number_of_breakdown":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_present":
                value_tab = f"{key}\t{value}"
            elif key == "Device_area_um2":
                value_tab = f"{key}\t{value}"
            elif key == "PUND_number":
                value_tab = f"{key}\t{value}"
            else:
                if value is None:
                    value_tab = "NA"
                else:
                    value_tab = value.replace(":","\t")

            if value_tab is not None:
                values_list.append(value_tab) 
                values_list.append("\n")  # Add a newline after each metadata entry
            else:
                continue


        # Write metadata header then the table
        with open(csv_filename, 'w', newline='') as f:
            f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
        Dataframe.to_csv(csv_filename, index=False, sep='\t', mode='a') 


