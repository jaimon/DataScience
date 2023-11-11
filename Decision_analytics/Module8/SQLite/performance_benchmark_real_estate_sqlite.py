import pandas as pd
import sqlite3
import time

# Define the location where you want to create the database file
db_file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/SQLite/performance_benchmark_real_estate_sales_sqlite.db'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/Jai/Desktop/Data/Real_Estate_Sales_2001-2020_GL.csv')

# Establish a connection to the database and create the table
conn = sqlite3.connect(db_file_path)
df.to_sql('real_estate_sales', conn, if_exists='replace')

cur = conn.cursor()

conn.commit()
#conn.close()


# Define your queries
queries = [
    'SELECT * FROM real_estate_sales;',
    'SELECT sum(Sale_Amount),Town FROM real_estate_sales GROUP BY Town;',
    'SELECT * FROM real_estate_sales WHERE Serial_Number = \'2020348\';',
    'select distinct a.* from real_estate_sales a;' 
]
#conn.close()

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
