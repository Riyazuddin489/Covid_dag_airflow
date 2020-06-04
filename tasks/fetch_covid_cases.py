import requests
import pandas as pd
import datetime as dt


API_URL = "https://api.covid19india.org/states_daily.json"


def fetch_daily_data(**args):
    """
    this method is used to fetch
    :param args: dict, this argument dictionary contains dag instance and pipeline running date.
    """
    pipeline_date = dt.datetime.strptime(args['pipeline_date'], '%Y-%m-%d')
    yesterday_date = pipeline_date.strftime('%d-%b-%y')
    res = requests.get(API_URL)
    res = res.json()
    pandas_df = pd.DataFrame(res['states_daily'])
    pandas_df = pandas_df[pandas_df['date'] == yesterday_date]
    # converting columns into rows
    pandas_df = pandas_df.melt(id_vars=["date", "status"],
                               var_name="state",
                               value_name="count"
                               )

    pandas_df['date'] = pd.to_datetime(pandas_df['date'], format="%d-%b-%y").dt.date
    pandas_df = pandas_df.rename(columns={'date': 'DateStr', 'state': 'State', 'count': 'Count',
                                          'status': 'Status'})
    pandas_df = pandas_df[['DateStr', 'State', 'Count', 'Status']]
    pandas_df.to_csv('./output/CSVs/'+pipeline_date.strftime('%Y-%m-%d')+'.csv', index=False)
    print('CSV generated successfully!!')
    args['ti'].xcom_push(key='csv_row_count', value=len(pandas_df))