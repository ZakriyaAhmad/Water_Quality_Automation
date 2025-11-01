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
file_name = 'Colne_INCA-P.csv'
SCHEMA_NAME = ''
table_name = 'colne_inca_p_scenerio'
# Function to read data from S3 and create table in the specified schema in PostgreSQL
def process_colne_p_s3_to_pgadmin():
    s3_client = boto3.client('s3', aws_access_key_id=s3_access_key_id, aws_secret_access_key=s3_secret_access_key, region_name=region_name)

    # Get the data from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}")
    data = response['Body'].read().decode('utf-8')

    # Convert the CSV content to a pandas DataFrame
    lines = data.strip().split('\n')
    headers = lines[0].split(',')  # Assuming your data in S3 is in CSV format, change delimiter accordingly if needed
    headers = [header.replace('%', '') for header in headers]
    headers = ['"'+header+'"' if ' ' in header else header for header in headers]
    rows = [tuple(line.split(',')) for line in lines[1:]]

    # Connect to PostgreSQL
    conn = main()

    # Open a cursor to perform database operations
    cursor = conn.cursor()
    truncate_query = "TRUNCATE TABLE colne_inca_p_scenerio"
    cursor.execute(truncate_query)
    # Construct the INSERT query
    # Prepare the query for data insertion
    insert_query = f"INSERT INTO colne_inca_p_scenerio (discharge, volume, velocity, water_depth, stream_power, shear_velocity, max_ent_grain_size, moveable_bed_mass, entrainment_rate, deposition_rate, bed_sediment, suspended_sediment, diffuse_sediment, water_column_tdp, water_column_pp, wc_sorption_release, stream_bed_tdp, stream_bed_pp, bed_sorption_release, macrophyte_mass, epiphyte_mass, water_column_tp, water_column_srp, water_temperature, tdp_input, pp_input, water_column_epc0, stream_bed_epc0, suspended_sediment_mass, mprop, settling_velocity, r, rmax, live_phytoplankton, dissolved_oxygen, bod, _saturation, reach, date_) VALUES %s"
    print(insert_query)

    # Execute the INSERT query with the data
    execute_values(cursor, insert_query, rows)

    # Commit the changes and close the cursor and connection
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Data  has been successfully loaded into the aquascope_mvp_bkp.colne_inca_n table.")

