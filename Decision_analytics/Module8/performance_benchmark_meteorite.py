
import psycopg2
import time 

# Define your connection parameters
params = {
    'database': 'Meteorite_landings',
    'user': 'postgres',
    'password': 'jimbo',
    'host': 'localhost',
    'port': 5432
}

# CSV file path
csv_file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/Meteorite_Landings.csv'

# PostgreSQL table name
table_name = 'public.meteorite_landings'

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
    'SELECT * FROM public.meteorite_landings;',
    'SELECT SUM(mass) as total_mass,name FROM public.meteorite_landings GROUP BY NAME;',
    'SELECT * FROM public.meteorite_landings WHERE name = \'Aachen\';',
    'select distinct a.* from public.meteorite_landings a;' 
]


# Number of times you want to run each query
num_runs = 100

# Store the total time for each query
total_times = [0] * len(queries)

# Run each query num_executions times
for i, query in enumerate(queries):
    print(f"Running query {i+1}...")
    for _ in range(num_runs):
        start_time = time.time()  # Start timing
        cur.execute(query)        # Execute the query
        end_time = time.time()    # End timing

        # Update the total time for this query
        total_times[i] += (end_time - start_time)

    # Calculate the average time for this query
    average_time = total_times[i] / num_runs
    print(f"Average runtime for query {i+1}: {average_time:.4f} seconds")


# Close the cursor and connection
cur.close()
conn.close()





