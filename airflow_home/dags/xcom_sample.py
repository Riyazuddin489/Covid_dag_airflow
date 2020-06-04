import datetime as dt
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


def send_value(**context):
    print('hello x_com fetching value')
    # argument ti here will be task_instance for current running dag
    context['ti'].xcom_push(key='k1', value='my_value')


def get_value(**context):
    print('hello x_com getting value')
    my_v = context['ti'].xcom_pull(dag_id='xcom_sample', key='k1')
    print('the value of previous task', my_v)


default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2020, 6, 1, 10, 00, 00),
    'concurrency': 1,
    'depends_on_past': True,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG('xcom_sample', default_args=default_args, schedule_interval='*/1 * * * *')as dag:

    task_push_data = PythonOperator(task_id='push_data',
                                    python_callable=send_value,
                                    # this will send context inside the above function as
                                    # argument with name 'ti' as task_instance
                                    provide_context=True
                                    )
    task_pull_data = PythonOperator(task_id='pull_data',
                                    python_callable=get_value,
                                    provide_context=True,
                                    )

    task_push_data>>task_pull_data