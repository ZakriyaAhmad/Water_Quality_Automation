from dbconnection_Scenerio import main 
import boto3
import psycopg2
from io import StringIO
import itertools
from psycopg2.extras import execute_values



# AWS S3 credentials and bucket information
s3_access_key_id = ''
s3_secret_access_key = ''
region_name = 'eu-west-1' 
bucket_name = ''
folder_name = 'Transform-CSV-Files'
file_name = 'Colne_INCA-N.csv'
SCHEMA_NAME = ''
table_name = 'colne_inca_n_scenerio'
# s3://persist-inca-automation/current-csv-files/Colne_INCA-N.csv
# Function to read data from S3 and create table in the specified schema in PostgreSQL
def process_colne_n_s3_to_pgadmin():
    s3_client = boto3.client('s3', aws_access_key_id=s3_access_key_id, aws_secret_access_key=s3_secret_access_key, region_name=region_name)

    # Get the data from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}")
    data = response['Body'].read().decode('utf-8')

    # Split the data into lines and extract headers and rows
    lines = data.strip().split('\n')
    headers = lines[0].split(',')  # Assuming your data in S3 is in CSV format, change delimiter accordingly if needed
    rows = [tuple(line.split(',')) for line in lines[1:]]

    # Connect to PostgreSQL
    conn = main()

    # Open a cursor to perform database operations
    cursor = conn.cursor()
    truncate_query = "TRUNCATE TABLE colne_inca_n_scenerio"
    cursor.execute(truncate_query)
    # Construct the INSERT query
    insert_query = f"INSERT INTO colne_inca_n_scenerio ({','.join(headers)}) VALUES %s"
    print(insert_query)

    # Execute the INSERT query with the data
    execute_values(cursor, insert_query, rows)

    # Commit the changes and close the cursor and connection
    conn.commit()
    cursor.close()
    conn.close() 

    print(f"Data  has been successfully loaded into the aquascope_mvp_bkp.colne_inca_n table.") 
    

