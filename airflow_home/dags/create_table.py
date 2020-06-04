from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.contrib.operators.bigquery_operator import BigQueryOperator, BigQueryCreateEmptyDatasetOperator,\
    BigQueryCreateEmptyTableOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

# config varibales
dag_config = Variable.get("bigquery_variables", deserialize_json=True)
BQ_CONN_ID = dag_config["bq_conn_id"]
BQ_PROJECT = dag_config["bq_project"]
BQ_TABLE = dag_config["bq_table"]
BQ_DATASET = dag_config["bq_dataset"]
default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2018, 12, 1),
    'end_date': datetime(2018, 12, 2),
    'email': ['airflow@airflow.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

schedule_interval = " 00 10 * * *"
dag = DAG(
    'create_covid_19_table',
    default_args=default_args,
    schedule_interval=schedule_interval
)

# # Task : check that the hacker news table contains data for that date.
# # for checkOperator if number of rows return grater than 0 then it will success, otherwise failure
# task = BigQueryCheckOperator(
#         task_id='bq_check_hackernews_full',
#         sql='''
#         #standardSQL
#         SELECT
#           FORMAT_TIMESTAMP("%Y%m%d", timestamp ) AS date
#         FROM
#           `bigquery-public-data.hacker_news.full`
#         WHERE
#           type = 'story'
#           AND FORMAT_TIMESTAMP("%Y%m%d", timestamp ) = "{{ yesterday_ds_nodash }}"
#         LIMIT
#           1
#         ''',
#         use_legacy_sql=False,
#         bigquery_conn_id=BQ_CONN_ID,
#         dag=dag
#     )

## Task : create a github daily metrics partition table
# BigQueryOperator is used to run queries on google BigQuery tables and store its result into another table.
# always use standard sql (i.e set legacy sql to false)
# task = BigQueryOperator(
#         task_id='bq_write_to_github_daily_metrics',
#         sql='''
#         #standardSQL
#         SELECT
#           date,
#           repo,
#           SUM(IF(type='WatchEvent', 1, NULL)) AS stars,
#           SUM(IF(type='ForkEvent',  1, NULL)) AS forks
#         FROM (
#           SELECT
#             FORMAT_TIMESTAMP("%Y%m%d", created_at) AS date,
#             actor.id as actor_id,
#             repo.name as repo,
#             type
#           FROM
#             `githubarchive.day.{{ yesterday_ds_nodash }}`
#           WHERE type IN ('WatchEvent','ForkEvent')
#         )
#         GROUP BY
#           date,
#           repo
#         ''',
#         destination_dataset_table='{0}.{1}.github_daily_metrics${2}'.format(
#             BQ_PROJECT, BQ_DATASET, '{{ yesterday_ds_nodash }}'
#         ),
#         write_disposition='WRITE_TRUNCATE',
#         allow_large_results=True,
#         use_legacy_sql=False,
#         bigquery_conn_id=BQ_CONN_ID,
#         dag=dag
#     )


# task1 create a new dataSet.
task1 = BigQueryCreateEmptyDatasetOperator(
    task_id='bq_create_new_dataset',
    dag=dag,
    dataset_id=BQ_DATASET,
    bigquery_conn_id=BQ_CONN_ID,
    project_id=BQ_PROJECT,
    dataset_reference={"friendlyName": BQ_DATASET}
)

# task2 create a new covid_19 partition table.
task2 = BigQueryCreateEmptyTableOperator(
    task_id='bq_create_new_talble',
    dag=dag,
    dataset_id=BQ_DATASET,
    table_id=BQ_TABLE,
    project_id=BQ_PROJECT,
    bigquery_conn_id=BQ_CONN_ID,
    schema_fields=[{"name": "DateStr", "type": "DATE", "mode": "REQUIRED"},
                   {"name": "State", "type": "STRING", "mode": "REQUIRED"},
                   {"name": "Count", "type": "INTEGER", "mode": "REQUIRED"},
                   {"name": "Status", "type": "STRING", "mode": "REQUIRED"}],
    time_partitioning={"type": "DAY", "field": "DateStr", "expiration_ms": "5184000000"}
    # partition expiration 60 days
)

task1 >> task2
