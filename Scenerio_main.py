import paramiko, psycopg2
import boto3
import time,pandas as pd
from Colne_N_Edit_Param import transform_Colne_N
from Colne_P_Edit_Param import transform_Colne_P
from run_model_Scenerio import run_ssh_commands
from s3_upload_Scenerio import transfer_to_s3_via_ssh
from Colne_INCA_P_Transform_Scenerio import Colne_INCA_P_transforamtion
from Colne_INCA_N_Transform_Scenerio import Colne_INCA_N_transforamtion
from Colne_N_Ingestion_Scenerio import process_colne_n_s3_to_pgadmin
from Colne_P_Ingestion_Scenerio import process_colne_p_s3_to_pgadmin
from db_ingestion_Scenerio_Dag import run_queries
from dbconnection_Scenerio import main
from Remove_All_Files import run_ssh_command


# # Replace with your AWS credentials or use IAM roles and instance profiles
aws_access_key_id = ''
aws_secret_access_key = ''
region_name = 'eu-west-1'  
bucket_name = 'p'

# # Replace these values with your EC2 instance details
hostname = '' 
username = 'ubuntu'
private_key_path = r"" 
# private_key_path = r"" 


#connect with database
db = main()
cursor=db.cursor()
query = f"""Select * FROM Colne_landuse_params where Status = 'Pending';"""
cursor.execute(query)
user_info = cursor.fetchall()
user_info_df = pd.DataFrame(user_info)
for index, row in user_info_df.iterrows():
    area = row[0]
    land_space_elements = [row[1], row[2], row[3], row[4], row[5]]
    use_case = row[7]
    user_id = row[6] 
    reach = row[9] 
    Discharge =  row[10]
    Abstraction =  row[11] 
    
    transform_Colne_N(reach,area,land_space_elements,Discharge,Abstraction)
    transform_Colne_P(reach,area,land_space_elements,Discharge,Abstraction)

    ec2_colne_persist_destination_directory = '/home/ubuntu/automation/Persist/Colne_INCA.dat'

    INCA_Colne_Model_Path = '/home/ubuntu/scenerio_automation/Colne/'
    INCA_output_path = '/home/ubuntu/scenerio_automation/output/'

    command = """rm -f /home/ubuntu/scenerio_automation/output/*"""
    run_ssh_command(hostname, username, private_key_path, command)
    
    command_to_execute_colne_INCA_N = f"wine {INCA_Colne_Model_Path}inca_n_cmd.exe -par {INCA_Colne_Model_Path}Colne_INCA-N.par -dat {ec2_colne_persist_destination_directory} -out {INCA_output_path}Colne_INCA-N.dsd"

    command_to_execute_colne_INCA_p  = f"wine {INCA_Colne_Model_Path}inca_pox_cmd.exe -par {INCA_Colne_Model_Path}Colne_INCA-P.par -dat {ec2_colne_persist_destination_directory} -out {INCA_output_path}Colne_INCA-P.dsd"

    File1 = 'Colne_INCA-N.dsd'
    File2 = 'Colne_INCA-N.stats'
    File3 = 'Colne_INCA-P.dsd'
    File4 = 'Colne_INCA-P.stats'
    #Call the function to Run INCA Models. 
    print('Run-N-Function')
    run_ssh_commands(hostname, username, private_key_path, command_to_execute_colne_INCA_N,File1,File2,INCA_output_path)
    print('Run-P-Function')
    run_ssh_commands(hostname, username, private_key_path, command_to_execute_colne_INCA_p,File3,File4,INCA_output_path)

 
    # Upload the files to S3 Bucket 
    transfer_to_s3_via_ssh()  

    #transform files to csv
    Colne_INCA_P_transforamtion()
    Colne_INCA_N_transforamtion() 


    #ingestion to test schema
    process_colne_p_s3_to_pgadmin()
    process_colne_n_s3_to_pgadmin() 

    #final queries
    run_queries(use_case,user_id)
    
    try:
        connection = main()
        cursor=connection.cursor()
        query = f"""update "AquaScope_MVP".Colne_landuse_params set Status = 'Activated' 
        where Status = 'Pending'  and userid = '{user_id}' and Scenerio_name = '{use_case}' 
        and reach = '{reach}' """
        print(query)
        cursor.execute(query)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
                print("Error executing queries:", error)
    finally:
            if connection:
                cursor.close()
                connection.close()
                print("Connection closed.") 
   
    

