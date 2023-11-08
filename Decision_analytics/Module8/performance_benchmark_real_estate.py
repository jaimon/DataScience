# %%
import psycopg2
import time 

# Define your connection parameters
params = {
    'database': 'Real_Estate',
    'user': 'postgres',
    'password': 'jimbo',
    'host': 'localhost',
    'port': 5432
}

# CSV file path
csv_file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/Real_Estate_Sales_2001-2020_GL.csv'

# PostgreSQL table name
table_name = 'public.real_estate_sales'

# Connect to PostgreSQL
conn = psycopg2.connect(**params)
cur = conn.cursor()

# Open the CSV file
with open(csv_file_path, 'r') as f:
    # Skip the header row
    next(f)
    # Use copy_expert to copy data from CSV to a table
    cur.copy_expert(sql=f"COPY {table_name} FROM STDIN WITH CSV", file=f)

# Commit changes
conn.commit()


# Define your queries
queries = [
    'SELECT * FROM public.real_estate_sales;',
    'SELECT sum(Sale_Amount),Town FROM public.real_estate_sales GROUP BY Town;',
    'SELECT * FROM public.real_estate_sales WHERE Serial_Number = \'2020348\';',
    'select distinct a.* from public.real_estate_sales a;' 
]

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


