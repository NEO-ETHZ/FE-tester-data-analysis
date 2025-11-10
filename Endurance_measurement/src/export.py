
import os
import pandas as pd
import csv

#Function that help to export the data in csv format
#It requires a dictionary with metadata information to be stored as header
#BE CAREFUL metadata_dict_DHM is a pandas dataframe and not a dicitonary....

def export_csv_DHM(Dataframe, metadata_dict_DHM, output_path, base_name):

    if len(Dataframe) == len(metadata_dict_DHM):
        # We store the csv in the csv folder in the main result folder
        output_csv_data_path = os.path.join(output_path, "CSV_data")
        os.makedirs(output_csv_data_path, exist_ok=True)  # Ensure output directory exists


        # We couple the dataframe with its corresponding metadata row
        for i, df in enumerate(Dataframe):
            
            # We recover the i line of the pd dataframe
            metadata_row = metadata_dict_DHM.iloc[i]
            csv_filename = os.path.join(output_csv_data_path, f"{base_name}_DHM.csv")

            # We store the string values of the metadata dictionary into a list and we replace ":" by tab
            values_list = []
            for value in metadata_row:
                value_tab = value.replace(":","\t")
                values_list.append(value_tab) 


            # Write metadata header then the table
            with open(csv_filename, 'w', newline='') as f:
                f.write("".join(values_list) + "\n\n")  # metadata and two empty rows
            df.to_csv(csv_filename, index=False, sep='\t', mode='a')

    else:
        print("Error: The number of dataframes does not match the number of metadata entries.")
                               




