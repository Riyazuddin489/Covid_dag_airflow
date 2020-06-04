
def find_percentage(**args):
    """
    this method is used to calculate percentage of rows uploaded.
    :param args: dict, this dictionary contains current dag instance.
    """
    total_rows = args['ti'].xcom_pull(dag_id='bq_covid_stats', key='csv_row_count')
    uploaded_rows = args['ti'].xcom_pull(dag_id='bq_covid_stats', key='big_table_row_count')
    print('uploaded rows count', uploaded_rows)
    print('csv rows', total_rows)
    try:
        total_percentage = (float(uploaded_rows)*100)/float(total_rows)
        print('percentage of rows uploaded today: ', str(total_percentage)+'%')
    except Exception as e:
        print(e)