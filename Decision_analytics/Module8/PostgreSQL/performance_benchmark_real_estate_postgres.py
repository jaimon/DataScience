import psycopg2
import time
import pandas as pd
from sqlalchemy import create_engine


# Define your connection parameters
params = {
    'database': 'Real_Estate',
    'user': 'postgres',
    'password': 'jimbo',
    'host': 'localhost',
    'port': 5432
}

# CSV file path
csv_file_path = '/Users/Jai/Desktop/Data/Real_Estate_Sales_2001-2020_GL.csv'

# SQLAlchemy engine
engine = create_engine(f'postgresql://{params["user"]}:{params["password"]}@{params["host"]}:{params["port"]}/{params["database"]}')

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Use pandas to create the table and copy data
df.to_sql('real_estate_sales', engine, if_exists='replace', index=False)


# Connect to PostgreSQL
conn = psycopg2.connect(**params)
cur = conn.cursor()

# Commit changes
conn.commit()


# Define your queries
queries = [
    'SELECT * FROM real_estate_sales where "List_Year"=\'2020\';',
    'SELECT sum("Sale_Amount"),"Town" FROM real_estate_sales where "List_Year"=\'2020\' GROUP BY "Town";',
    'SELECT * FROM real_estate_sales WHERE "List_Year"=\'2020\' and "Serial_Number" = \'2020348\';',
    'select distinct a.* from real_estate_sales a where "List_Year"=\'2020\';' 
]

# Number of times you want to run each query
num_runs = 100
query_averages = {}


try:
    for query in queries:
        run_times = []

        for _ in range(num_runs):
            start_time = time.perf_counter()

            cur.execute(query)
            cur.fetchall()
            end_time = time.perf_counter()

            run_times.append(end_time - start_time)

        average_run_time = sum(run_times)/num_runs
        query_averages[query] = average_run_time
finally:
    cur.close()
    conn.close()

for query, avg_time in query_averages.items():
    print(f"Query: {query}\nAverage Run Time: {avg_time:.4f} seconds\n")


