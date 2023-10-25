import random
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

# Sample data (simplified for the sake of the example)
n_counties = 83
n_districts = 14
county_populations = [random.randint(10000, 300000) for _ in range(n_counties)]
avg_district_population = sum(county_populations) / n_districts  # desired avg population per district

# Create a new LP problem
model = LpProblem("Michigan_Redistricting", LpMinimize)

# Decision variable: x[i][j] is 1 if county i is assigned to district j, 0 otherwise
x = [[LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n_districts)] for i in range(n_counties)]

# Objective: Minimize the number of counties that are assigned to multiple districts
model += lpSum(x[i][j] for i in range(n_counties) for j in range(n_districts)) - n_counties

# Constraint: Each county is assigned to exactly one district
for i in range(n_counties):
    model += lpSum(x[i][j] for j in range(n_districts)) == 1

# Constraint: Each district has approximately the same population (within some tolerance)
tolerance = 5000  # For example, allow districts to be within 5000 of the average
for j in range(n_districts):
    district_counties = [i for i in range(n_counties) if x[i][j].varValue == 1]
    print(f"District {j+1} contains counties: {district_counties}")