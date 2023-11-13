This research utilizes benchmarking to solve the managerial problem of deciding whether PostgreSQL or SQLite, two key players in the DBMS space, is a better choice for a business and its specific requirements. 
The benchmarking study compares the run-time performance of two DBMSs—PostgreSQL and SQLite—by performing a series of frequently used SQL queries, including GROUP BY, WHERE, and SELECT DISTINCT clauses.
The data sources used for the benchmark comparisons between the DBMSs are the below:

https://catalog.data.gov/dataset/electric-vehicle-population-data/resource/fa51be35-691f-45d2-9f3e-535877965e69

https://catalog.data.gov/dataset/real-estate-sales-2001-2018
- Note that this dataset was too large to run efficiently in either DBSM. As such, we filtered the records to only those with year = '2020' for processing comparison purposes.

https://catalog.data.gov/dataset/nyc-jobs 

https://catalog.data.gov/dataset/meteorite-landings 

Both DBMSs were subjected to 1600 query runs using these 4 databases, 4 queries per database, 100 runs per query—totaling 3200 query runs.
The output of each python script contains the average run time for each query across both the DBMSs. When assessing the results, 
PostgreSQL outperformed SQLite with lower average run times in 14 of the 16 distinct queries.
