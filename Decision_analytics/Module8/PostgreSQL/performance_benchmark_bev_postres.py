import psycopg2
import time
import pandas as pd
from sqlalchemy import create_engine

# Define your connection parameters
params = {
    'database': 'BEV',
    'user': 'postgres',
    'password': 'jimbo',
    'host': 'localhost',
    'port': 5432
}

# CSV file path
csv_file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module8/Data/Electric_Vehicle_Population_Data.csv'

# SQLAlchemy engine
engine = create_engine(f'postgresql://{params["user"]}:{params["password"]}@{params["host"]}:{params["port"]}/{params["database"]}')

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Use pandas to create the table and copy data
df.to_sql('bev', engine, if_exists='replace', index=False)


# Connect to PostgreSQL
conn = psycopg2.connect(**params)
cur = conn.cursor()


# Commit changes
conn.commit()

# Define your queries
queries = [
    'SELECT * FROM electric_vehicle_pop_data;',
    'SELECT COUNT(*),County FROM electric_vehicle_pop_data GROUP BY County;',
    'SELECT * FROM electric_vehicle_pop_data WHERE County = \'Yakima\';',
    'select distinct a.* from electric_vehicle_pop_data a;' 
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





