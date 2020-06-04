from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

GOOGLE_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


def use_dataset(dataset_id):
    """
    this method is used to fetch dataSet reference.
    :param dataset_id: string, big query dataSet id.
    :return: dataSet reference, google client.
    """
    path = './config/BigQueryProject-38532f2e6a07.json'
    credentials = service_account.Credentials.from_service_account_file(
        path, scopes=[GOOGLE_SCOPE])
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id)

    dataset_ref = client.dataset(dataset_id)
    # creating dataSet if not exists
    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset = client.create_dataset(dataset)
        print('Dataset {} created.'.format(dataset.dataset_id))
    finally:
        return dataset_ref, client


def upload_csv_to_big_table(**args):
    """
    this method is used to upload csv to big table in google cloud.
    :param args: dict, this dictionary contains dag instance, dataSet id, new partition date, new csv file name and table id .
    """
    print(args['partition_date'])
    dataset_ref, client = use_dataset(args['dataset_id'])
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.schema_update_options = ['ALLOW_FIELD_ADDITION', 'ALLOW_FIELD_RELAXATION']
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    job_config.skip_leading_rows = 1
    # to fetch data and insert data from a particular partition of a given bigTable partition table
    # we have to use this syntax 'table_name$YYYYMMDD' where 'YYYYMMDD' is date is in case of date partition
    table_ref = dataset_ref.table(args['table_id']+"$"+args['partition_date'])
    filename = './output/CSVs/{}.csv'.format(args['file_date'])
    with open(filename, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    try:
        job.result()  # Waits for table load to complete.
        print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_ref, table_ref))
        args['ti'].xcom_push(key='big_table_row_count', value=job.output_rows)
    except Exception as e:
        print(e)
