from datetime import timedelta
from airflow import DAG
import os
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'Zakriya Ahmad',
    'depends_on_past': True,
    'start_date': days_ago(2),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'Scenerio_Task_Automation',
    default_args=default_args,
    description='Email Alert Automation',
    schedule_interval='0 3 * * *',
    catchup=False,
) 
   
current_dir = os.path.dirname(__file__) 


t1 = BashOperator(
        task_id = 'Scenerio_Task_Automation', 
    params = {
        'wk_dir' : os.path.abspath(os.path.join(__file__,'../'))
    },
    depends_on_past = False,
    bash_command = "python3 {{ params.wk_dir }}/Scenerio_main.py -vvv",
    dag = dag
) 

t1