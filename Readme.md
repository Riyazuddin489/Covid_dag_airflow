## Introduction
```
Airflow pipeline to fetch daily new covid cases data for indian states and store them into google BigTable.

```
## Setup Airflow
1. first install Airflow in your system.
  `pip install apache-airflow`
2. install google cloud dependency for this project.
  `pip install 'apache-airflow[gcp]'`
3. check airflow version to ensure if it is successfully installed.
    `airflow version`
4. create a airflow_home folder.
5. then set Airflow path: 
    *   go to the folder where you created `airflow_home` folder.
    *   open terminal there and set airflow_path using this command
        `export AIRFLOW_HOME=$(pwd)/airflow_home`
6. then write `airflow initdb`. It will create airflow database, logs and unittest file.
7. then create a `dags` folder inside airflow_home folder to store our dags.
8. now to start server run the commands below:
    *   `airflow webserver`
    *   `airflow scheduler`
9. now to go to `localhost:8080` in your browser you will see some example dags there.

Note: If you face any sqlite related database exception while running the server, then run `airflow initdb` command again.  



## How to run project on local laptop

Follow the guide here to ensure you run correct main file:
    
*   first create a json credentials for google bigQuery api and paste them into config folder.
*   create a google cloud service connection inside your airflow.
*   create variable in airflow using the json inside config/Airflow_variables folder.
*   paste project dags inside your dag folder in airflow_home folder.
*   (optional) you can create dataSet and table on google bigQuery using `create_table` dag.
*   main dag files to run `covid_19_statewise_bq_table.py`.
## Screenshots

![alt text](output/pics/1.png?raw=true "database schema")
![alt text](output/pics/2.png?raw=true "data preview")
![alt text](output/pics/3.png?raw=true "pipeline preview")
![alt text](output/pics/4.png?raw=true "upload percentage")
![alt text](output/pics/5.png?raw=true "graph view")
