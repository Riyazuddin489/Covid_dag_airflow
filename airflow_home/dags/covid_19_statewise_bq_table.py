from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta, datetime
from tasks.fetch_covid_cases import fetch_daily_data
from tasks.find_upload_percentage import find_percentage
from tasks.upload_csv_to_big_table import upload_csv_to_big_table
import yaml

# #fetching constants

# from airflow
dag_config = Variable.get("bigquery_variables", deserialize_json=True)
BQ_CONN_ID = dag_config["bq_conn_id"]
BQ_PROJECT = dag_config["bq_project"]
BQ_TABLE = dag_config["bq_table"]
BQ_DATASET = dag_config["bq_dataset"]

# form config yaml file
with open("config/pipelines/covid_pipeline.yaml", 'r') as stream:
    try:
        dag_info = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# form lib yaml file
with open("lib/pipeline_defaults.yaml", 'r') as stream:
    try:
        dag_defaults = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

"""covid dag configuration arguments."""
default_args = {
    'owner': dag_defaults['covid_19_statewise_bq_table_production']['pipeline_owner'],
    'start_date': datetime.strptime(dag_info['covid_19_statewise_bq_table_staging']['start_date'], "%Y-%m-%d %H:%M:%S"),
    'concurrency': 1,
    'depends_on_past': True,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': int(dag_info['covid_19_statewise_bq_table_staging']['retries']),
    'retry_delay': timedelta(seconds=5),

}

with DAG(dag_info['covid_19_statewise_bq_table_staging']['dag_id'], default_args=default_args,
         schedule_interval=dag_info['covid_19_statewise_bq_table_staging']['schedule_interval'])as dag:

    task1 = PythonOperator(task_id='create_csv',
                           python_callable=fetch_daily_data,
                           # execution_date is airflow variable which returns current execution date in python format.
                           # fetching yesterday's date.
                           op_kwargs={'pipeline_date': '{{ (execution_date - '
                                                       'macros.timedelta(days=1)).strftime("%Y-%m-%d")}}'},
                           provide_context=True)

    # another approach is create external table from csv using BigQueryCreateExternalTableOperator
    # and then query above records and insert into partition table using BigQueryOperator and use table name in this
    # format while inserting data 'project_id.dataSet_name.table_name$partition_date'
    # example 'project-123.myDataSet.myTable$20200320'
    task2 = PythonOperator(task_id='upload_data',
                           python_callable=upload_csv_to_big_table,
                           op_kwargs={'table_id': BQ_TABLE,
                                      'dataset_id': BQ_DATASET,
                                      'file_date': '{{ (execution_date - macros.timedelta(days=1)).'
                                                   'strftime("%Y-%m-%d")}}',
                                      # provide yesterday execution date in YYYYMMDD format
                                      'partition_date': '{{yesterday_ds_nodash}}'
                                      },
                           provide_context=True)

    task3 = PythonOperator(task_id='upload_percentage',
                           python_callable=find_percentage,
                           provide_context=True
                           )

    task1.set_downstream(task2)
    task2.set_downstream(task3)
    # or we can specify flow like this
    # task1 >> task2 >> task3
