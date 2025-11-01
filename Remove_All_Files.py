import paramiko
import boto3
import time,os


hostname = '' 
username = 'ubuntu'
# ec2_key_path = r"D:\Automation\Automation.pem"
private_key_path = r"/home/ubuntu/automation.pem" 
aws_access_key_id = ''
aws_secret_access_key = '/XDPeR'
region_name = 'eu-west-1' 

def run_ssh_command(hostname, username, private_key_path, command):
    try:
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure and should not be used in production)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key (you may need to adjust the key permissions)
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

        # Connect to the EC2 instance
        ssh_client.connect(hostname=hostname, username=username, pkey=private_key)

        # Execute the command and capture the output
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Print the command output
        print("Command output:")
        # print(stdout.read().decode())
        
        # # Print the command error (if any)
        # print(stderr.read().decode())
        print("Command END")
        ssh_client.close()
        
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print("Error occurred while connecting to the server:", e)
