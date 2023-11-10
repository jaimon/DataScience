import pandas as pd
import sqlite3
import time

# Define the location where you want to create the database file
db_file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/SQLite/performance_benchmark_bev_sqlite.db'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/Data/Electric_Vehicle_Population_Data.csv')

# Establish a connection to the database and create the table
conn = sqlite3.connect(db_file_path)
df.to_sql('electric_vehicle_pop_data', conn, if_exists='replace')

cur = conn.cursor()

conn.commit()
#conn.close()


# Define your queries
queries = [
    'SELECT * FROM electric_vehicle_pop_data;',
    'SELECT COUNT(*),County FROM electric_vehicle_pop_data GROUP BY County;',
    'SELECT * FROM electric_vehicle_pop_data WHERE County = \'Yakima\';',
    'select distinct a.* from electric_vehicle_pop_data a;'
]
#conn.close()

# Number of times you want to run each query
num_runs = 100
query_averages = {}

try:
    for query in queries:
        run_times = []

        for _ in range(num_runs):
            start_time = time.time()
            cur.execute(query)
            end_time = time.time()
            run_times.append(end_time - start_time)

        average_run_time = sum(run_times)/num_runs
        query_averages[query] = average_run_time
finally:
    cur.close()
    conn.close()

for query, avg_time in query_averages.items():
    print(f"Query: {query}\nAverage Run Time: {avg_time:.4f} seconds\n")
