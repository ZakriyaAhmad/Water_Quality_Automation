import os
import pandas as pd
import numpy as np
import boto3
from io import StringIO

# Replace with your AWS credentials or use IAM roles and instance profiles
aws_access_key_id = 'AKIA3YZJKPFW6AFKH4M4'
aws_secret_access_key = 'Yqf50oTXj6F8qNfKrjqoxyuGZZGayVab4x/XDPeR'
region_name = 'eu-west-1'  
source_bucket_name = 'scenerio-automation'
source_file_key = 'inca-model-output-files/Colne_INCA-P.dsd'  # Replace with the path of the source file in the source S3 bucket
destination_bucket_name = 'scenerio-automation'
destination_file_key = 'Transform-CSV-Files/Colne_INCA-P.csv'# Replace with the path of the destination file in the destination S3 bucket

# Initialize the S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)

def read_s3_file_as_dataframe(bucket, key):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    return pd.read_csv(StringIO(data.decode('cp1252')), delimiter="\s\s+", skiprows=[0, 1, 2, 3, 4, ])

def upload_dataframe_to_s3(dataframe, bucket, key):
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())

def Colne_INCA_P_transforamtion():
    try:
        # Read the file from the source S3 bucket as a DataFrame
        d1 = read_s3_file_as_dataframe(source_bucket_name, source_file_key)

        # Your data transformation code here (same as in your original code)
        df = d1.drop(labels=0, axis=0)
        df = df.drop(labels=1, axis=0)
        df.reset_index(inplace=True)
        df.drop(columns='index', inplace=True)
        sb_c = df.loc[df['Discharge'].str.contains("Reach ", case=False)]
        sb_c['Discharge'] = sb_c['Discharge'].str.replace('Reach ', '')

        f_t = 'TR01'

        df['Reach'] = np.nan
        df['Date'] = pd.date_range(start='2010-01-01', periods=len(df), freq='D')
        df['Reach'].fillna(value=f_t, inplace=True)

        # populate the Reach and Date columns
        p=1
        index_del = []
        for i in sb_c['Discharge']:
            ind = sb_c.index[sb_c['Discharge'] == i].tolist()
            r1 = ind[0]+1
            r2 = ind[0]+2
            r3 = ind[0]+3
            index_del.append(ind[0])
            index_del.append(r1)
            index_del.append(r2)
            index_del.append(r3) 

            fw = i.split()
            fw = fw[0]
            if p == 1:
                df['Reach'].iloc[0:ind[0]] = f_t
                df['Date'].iloc[0:ind[0]] = pd.date_range(start='2010-01-01', periods=ind[0], freq='D')
            elif p > 0 and p < (len(sb_c['Discharge'])+1):
                df['Reach'].iloc[pre[0]+1:ind[0]] = pre_fw
                df['Date'].iloc[pre[0]+1:ind[0]] = pd.date_range(start='2010-01-01', periods=(ind[0]-pre[0]-1), freq='D')
                if p == (len(sb_c['Discharge'])):
                    df['Reach'].iloc[ind[0]+1:] = fw
                    df['Date'].iloc[ind[0]+1:] = pd.date_range(start='2010-01-01', periods=(len(df)-ind[0]-1), freq='D')
            else:
                print('completed') 

            pre_fw = fw
            pre = ind
            p = p+1  
        df.drop(index_del, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df['Date'] = pd.Series(df['Date']).fillna(method='ffill')
        df.head()

        # Save the transformed DataFrame to a CSV file and upload it to the destination S3 bucket
        temp_csv_file = 'Colne_INCA-P_temp.csv'
        df.to_csv(temp_csv_file, index=False)  # Save to a temporary file

        # Upload the temporary CSV file to the destination S3 bucket
        upload_dataframe_to_s3(df, destination_bucket_name, destination_file_key)

        # Remove the temporary CSV file after uploading to S3
        os.remove(temp_csv_file)

        print(f"File '{source_file_key}' from S3 bucket '{source_bucket_name}' transformed and uploaded to '{destination_file_key}' in S3 bucket '{destination_bucket_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

