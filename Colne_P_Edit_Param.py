import os
import pandas as pd
import numpy as np
import boto3,paramiko
from io import StringIO

# Replace with your AWS credentials or use IAM roles and instance profiles
aws_access_key_id = 'AKIA3YZJKPFW6AFKH4M4'
aws_secret_access_key = 'Yqf50oTXj6F8qNfKrjqoxyuGZZGayVab4x/XDPeR'
region_name = 'eu-west-1'  
source_bucket_name = 'scenerio-automation'
source_file_key = 'prameters-files/Colne_INCA-P.par'  # Replace with the path of the source file in the source S3 bucket

# Replace these values with your EC2 instance details
hostname = '34.244.72.239' 
username = 'ubuntu'
private_key_path = r"/home/ubuntu/automation.pem" 
# private_key_path = r"D:\Automation\Automation.pem" 

# Initialize the S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)


def transform_Colne_P(reach,area,land_space_elements,Discharge,Abstraction):
    response = s3_client.get_object(Bucket=source_bucket_name, Key=source_file_key)
    data = response['Body'].read()
    df = pd.read_csv(StringIO(data.decode('cp1252')), delimiter="\s\s+")
    df = df.reset_index(drop=True)
    df = df.replace('\t', " ", regex=True)
    updated_rows = []
    land_space_elements = " ".join(map(str, land_space_elements))
    land_space_elements = [land_space_elements]

    # Flag to track if 'TR01' has been found and updated
    tr01_found = False
    # Process the content of the CSV file
    i = 0
    while i < len(df):
        if not tr01_found and reach in df.iloc[i].values:
            tr01_found = True
            try:

                #code to replace the land space user inputs area with param files
                df.iloc[i+2] = area
                
                #code to replace the land space user inputs elements with param files
                line_to_update_line_space_elements = df.iloc[i + 3]
                line_values = line_to_update_line_space_elements.str.split(' ')
                line_values.iloc[0][:5] = land_space_elements
                df.iloc[i + 3] = line_values
                update = df.iloc[i + 3]
                modified_series = ', '.join(map(str, update.iloc[0]))
                df.iloc[i + 3] = modified_series
             

                # # code to replace the discharge
                line_to_update_line_space_elements = df.iloc[i + 8]
                line_values = line_to_update_line_space_elements.str.split(' ')
                line_values[0][5] = Discharge
                line_values[0][6] = Abstraction
                df.iloc[i + 8] = line_values
                update = df.iloc[i + 8]
                modified_series = ' '.join(map(str, update.iloc[0]))
                df.iloc[i + 8] = modified_series
          
                 
                
            except ValueError:
                pass
        updated_rows.append(df.iloc[i].values)
        i += 1 
    par_file_path = 'Colne_INCA-P.par'
    # Save the DataFrame as a tab-delimited text file (.par)
    df.to_csv(par_file_path, sep='\t', index=False)
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
    client.connect(hostname=hostname, username=username, pkey=private_key)
    sftp = client.open_sftp()
    remote_path = f'/home/ubuntu/scenerio_automation/Colne/{par_file_path}'
    sftp.put(par_file_path, remote_path)
    sftp.close()
    print(f"File '{par_file_path}' uploaded to the EC2 instance at '{remote_path}'.")



