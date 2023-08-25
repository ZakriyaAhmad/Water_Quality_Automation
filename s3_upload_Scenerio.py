import boto3
import os
import paramiko

# Replace with your AWS credentials or use IAM roles and instance profiles
aws_access_key_id = 'AKIA3YZJKPFW6AFKH4M4'
aws_secret_access_key = 'Yqf50oTXj6F8qNfKrjqoxyuGZZGayVab4x/XDPeR'
region_name = 'eu-west-1'  

# Replace these with your EC2 instance details
ec2_instance_public_ip = '34.244.72.239'
ec2_username = 'ubuntu'
# ssh_identity_file =  r'D:\Automation\automation.pem' 

source_folder_path = '/home/ubuntu/scenerio_automation/output/'
ssh_identity_file = r"/home/ubuntu/automation.pem"
bucket_name = 'scenerio-automation'
destination_s3_key_prefix = 'inca-model-output-files/'

# Code to transfer files from EC2 to S3 Bucket

def transfer_to_s3_via_ssh():
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             region_name=region_name)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=ec2_instance_public_ip, username=ec2_username, key_filename=ssh_identity_file)
        sftp_client = ssh_client.open_sftp()

        # List all files in the source folder on the EC2 instance
        files_on_ec2 = sftp_client.listdir(source_folder_path)

        for file_name in files_on_ec2:
            # Download the file to a local temporary directory
            local_temp_file = f'./{file_name}'
            sftp_client.get(os.path.join(source_folder_path, file_name), local_temp_file)

            # Upload the file to S3 with the specified key prefix
            destination_s3_key = os.path.join(destination_s3_key_prefix, file_name)
            s3_client.upload_file(local_temp_file, bucket_name, destination_s3_key)

            # Remove the temporary local file
            os.remove(local_temp_file)

            print(f"File '{file_name}' transferred to S3 bucket '{bucket_name}' with key '{destination_s3_key}'.")

        # Close the SFTP connection
        sftp_client.close()

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print("Error occurred while connecting to the EC2 instance:", e)
    except Exception as e:
        print("An error occurred during the transfer:", e)


