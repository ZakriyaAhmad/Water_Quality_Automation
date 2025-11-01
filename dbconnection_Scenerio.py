import paramiko
import psycopg2
import sshtunnel
ssh_host = ""
ssh_port = 22
ssh_username = "ec2-user"
# ssh_identity_file = r"C:\Users\hp\Downloads\.pem"
ssh_identity_file = r"/home/ubuntu/.pem" 
db_host = ""
db_port = 5432
db_name = ""
db_username = "postgres"
db_password = ""
def create_ssh_tunnel():
    try:
        # Create an SSH tunnel 
        tunnel =   sshtunnel.SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_pkey=ssh_identity_file,
            remote_bind_address=(db_host, db_port)
        )
        # Start the SSH tunnel
        tunnel.start() 
        return tunnel 
        
    except Exception as e:
        print(e)


def main():
    ssh_conn = create_ssh_tunnel()

    # Update the database settings
    if ssh_conn:
        db = psycopg2.connect(
        database=db_name,
        user=db_username,
        password=db_password,
        host="127.0.0.1",
        port=ssh_conn.local_bind_port,
    ) 
        print('connection has been established successfully')
        return db
      
      
    
