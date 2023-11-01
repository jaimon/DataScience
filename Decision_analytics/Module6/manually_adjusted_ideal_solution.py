"""
MANUALLY ADJUSTED IDEAL SOLUTION

Model Approach:
    This approach to solving the optimization problem for the redistricting of congressional districts in
    the state of Michigan consisted of using the optimization model to guide the creation of manually 
    assigned districts.

    As counties were manually assigned to districts, it resulted in their being less decision variables for
    the model to optimize, thus reducing the complexity of the problem. With each iteration of manual 
    assignment, the model was able to give us a more optimal solution and further guide the next iteration
    of manual assignment.

    We used this approach to finding the ideal solution because of the difficulty we had with creating a 
    functioning contiguous contraint that required all the counties within a district to be connected. 

Outline of Methods Used for the Model:
- Objective Function:
    Minimize the deviation of population in each district from the average population ("the ideal population")

- Decision Variables:
    A binary variable that indicating whether a county is in a district or not

- Constraints:
    1. Each county must be assigned to exactly one district
    2. A county assigned to a district must be adjacent to at least one other county in that district
    3. The population of each district must be within 20% of the ideal population

NOTE: about the data files used for this model:
    Each of the data files used for this model are ammended with the label "mod" at the end of them to indicate
    that the counties that have two-word names were changed to one-word names. This was done to make the data
    easier to work with in the model. Specifially when it came to creating the adjacency matrix that is used
    for the adjacency constraint.

"""

### ----------------------------------------------------------------------------------------------------------

# STEP 1: Load the necessary packages
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from math import pi, pow, sin, cos, asin, sqrt, floor
from pulp import *

### ----------------------------------------------------------------------------------------------------------

# STEP 2: Read in the data files 

# Read in the Excel file of Michigan counties, their population, and their coordinates
xlsx_file_path = '/Users/stefanjenss/Desktop/DataScience/Decision_analytics/Module6/michigan_counties_mod.xlsx'
michigan_counties = pd.read_excel(xlsx_file_path)

# Read in the GeoJSON files of Michigan county boundaries
geojson_file_path = '/Users/stefanjenss/Desktop/DataScience/Decision_analytics/Module6/michigan_counties_mod.geojson'
michigan_counties_geojson = gpd.read_file(geojson_file_path)

# Set the file path for the txt file that contains the adjacency information for each county in the United States
txt_file_path = '/Users/stefanjenss/Desktop/DataScience/Decision_analytics/Module6/county_adjacency_mod.txt'

# Merge the Excel file and the GeoJSON file on the county name
michigan_counties_merged = michigan_counties.merge(michigan_counties_geojson, left_on='county_names', right_on='name', how='inner')
# Confirm that the merge was successful
print(michigan_counties_merged.head())

### ----------------------------------------------------------------------------------------------------------

#STEP 3: Create an adjacency matrix for the counties in Michigan using the information from the txt file

# 3.1 Store the Michigan counties and their adjacencies in a dictionary

# Create a list of the county names from michigan_counties_merged dataframe
county_names = michigan_counties_merged['county_names'].to_numpy()

# Parse the file to extract ajacies for Michigan counties
adjacency_data = {}
current_county = None

with open(txt_file_path, 'r') as file:
    for line in file:
        # Split the line based on tab delimiter
        parts = line.split('\t')
        # If the line contains a county name, update the current county
        if parts[0]:
            current_county_name = parts[0].replace('"', '').strip()
            # Check if the county is from Michigan
            if "MI" in current_county_name:
                current_county = current_county_name
                adjacency_data[current_county] = []
        # If there's a current county from Michigan, append the adjacent counties to it
        elif current_county:
            adjacent_county_name = parts[2].replace('"', '').strip()
            if "MI" in adjacent_county_name:  # Only consider MI counties as adjacent
                adjacency_data[current_county].append(adjacent_county_name)

# 3.2 Modify this dictionary so that only the county names e.g. "Alcona" are used as keys, and not the full county
#     names e.g. "Alcona County, MI"
modified_adjacency_dict = {}

for full_name, adjacents in adjacency_data.items():
    county_name = full_name.split()[0].replace('"', '')
    modified_adjacency_dict[county_name] = [adj.split()[0].replace('"', '') for adj in adjacents]

# 3.3 Create the adjacency matrix for Michigan counties using the modified adjacency dictionary
adjacency_matrix = pd.DataFrame(0, index = county_names, columns = county_names)

for county, adjacents in modified_adjacency_dict.items():
    for adjacent in adjacents:
        adjacency_matrix.loc[county, adjacent] = 1

# Display the first few rows of the adjacency matrix
print(adjacency_matrix.head())

### ----------------------------------------------------------------------------------------------------------

"""
Initial Manual Assignment of Counties to Districts:
    Prior to creating the optimization model, we were able to identify a number of counties that should be 
    assigned to their own districts based on large population size and/or geographic location.

    The counties that we idenfied we immediately large enough to be their own districts were:
        - Wayne County
        - Oakland County
        - Macomb County
    
    The counties that we identified as needing to be assigned to their own district based on geographic location
    were:
        These are the counties that are in the far north region of Michigan and have relatively low populations.
        - Alpena
        - Antrim
        - Baraga
        - Charlevoix
        - Cheboygan
        - Chippewa
        - Delta
        - Dickinson
        - Emmet
        - Gogebic
        - Houghton
        - Iron
        - Keweenaw
        - Luce
        - Mackinac
        - Marquette
        - Menominee
        - Montmorency
        - Ontonagon
        - Otsego
        - Presque Isle
        - Schoolcraft
"""

### ----------------------------------------------------------------------------------------------------------

# STEP 5: Create the inital optimization model (Round 1)

# 5.1 Define the parameters for the optimization model
# Create a dictionary of county names and their populations
county_populations = michigan_counties_merged[['name', 'pop2020']].set_index('name').to_dict()['pop2020']

# Number of counties and districts in Michigan
n_counties = 83
n_districts = 14

# 5.2 Create a list of the large counties and the northern counties that will be assigned to their own districts
# Create a list of the three large counties
large_counties = ['Wayne', 'Oakland', 'Macomb']

# Create a list of the counties in the upper peninsula of Michigan
northern = ["Alger", "Baraga", "Chippewa", "Delta", "Dickinson", "Gogebic", "Houghton", "Iron", "Keweenaw","Luce", "Mackinac", "Marquette", "Menominee", "Ontonagon", "Schoolcraft", "Emmet", "Cheboygan", "PresqueIsle", "Charlevoix", "Antrim", "Otsego", 
                        "Montmorency", "Alpena" ]

# Create a list of all the manually assigned counties
manual_counties = large_counties + northern #most_northern + second_most_northern

# Create a new dataframe that doesn't contain any of the manual counties
michigan_counties_adjusted = michigan_counties_merged[~michigan_counties_merged['name'].isin(manual_counties)]

# 5.3 Adjust the number of counties and districts and calculate the new ideal district population
# Adjust the number of counties and districts and the ideal district population
n_counties_adjusted = len(michigan_counties_adjusted)
n_districts_adjusted = n_districts - (len(large_counties) + 1)
average_district_population_adjusted = michigan_counties_adjusted['pop2020'].sum() / n_districts_adjusted

# Creat a dictionary of the adjusted county names and their populations
county_populations_adjusted = michigan_counties_adjusted[['name', 'pop2020']].set_index('name').to_dict()['pop2020']
county_names_adjusted = michigan_counties_adjusted['name'].to_numpy()

# Step 5.4 Create the optimization model
# Initialize the adjusted model
model1 = LpProblem("Michigan_Redistricting_Adjusted", LpMinimize)

# Decision variable: binary variable indicating whether a county is in a district
x1 = LpVariable.dicts("x_adjusted", ((i, j) for i in county_names_adjusted for j in range(n_districts_adjusted)), cat='Binary')

# Objective function: minimize the deviation of populations in each district from the average population
# Calculate the deviation of populations in each district from the average population
model1 += lpSum(
    ((county_populations_adjusted[county_names_adjusted[i]] - average_district_population_adjusted) *
     (county_populations_adjusted[county_names_adjusted[i]] - average_district_population_adjusted) *
     x1[(county_names_adjusted[i], j)])
    for i in range(len(county_names_adjusted))
    for j in range(n_districts_adjusted)
)

# Constraints
# Constraints: Each county must be assigned to exactly one district
for i in range(len(county_names_adjusted)):
    model1 += lpSum(x1[(county_names_adjusted[i], j)] for j in range(n_districts_adjusted)) == 1

# Adjacency constraint
for i in range(len(county_names_adjusted)):
     for j in range(n_districts_adjusted):
         model1 += lpSum(adjacency_matrix.loc[county_names_adjusted[i], neighbor] * x1[(neighbor, j)] for neighbor in county_names_adjusted) >= x1[(county_names_adjusted[i], j)]

# The population of the district must be within 20% of the average population
for j in range(n_districts_adjusted):
    model1 += lpSum(county_populations_adjusted[county_names_adjusted[i]] * x1[(county_names_adjusted[i], j)] for i in range(len(county_names_adjusted))) >= 0.80 * average_district_population_adjusted
    model1 += lpSum(county_populations_adjusted[county_names_adjusted[i]] * x1[(county_names_adjusted[i], j)] for i in range(len(county_names_adjusted))) <= 1.20 * average_district_population_adjusted

# Step 5.5 Solve the model
# Solve and print the solution
model1.solve()

# Print the status of the solution
print("Status:", LpStatus[model1.status])

# Print the objective value
print("Objective Function Value:", value(model1.objective))
print("")

# Print the district assignments along with the total district populations on a separate line starting with district 1
for j in range(n_districts_adjusted):
    print("District", j + 1, ":", end = " ")
    district_population = 0
    for i in range(len(county_names_adjusted)):
        if x1[(county_names_adjusted[i], j)].varValue == 1:
            print(county_names_adjusted[i], end = ", ")
            district_population += county_populations_adjusted[county_names_adjusted[i]]
    print("Total Population:", district_population)

# Manually assign the 'northern' counties in the upper peninsula to the same district
print("District 11:", northern)

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    print("District", i + 12, ":", large_counties[i])

### ----------------------------------------------------------------------------------------------------------

# STEP 6: Visualize the generated district assignment form the initial (round 1) optimization model to better 
# understand the partitioning of districts

# 6.1 Add a column to the michigan_counties_merged dataframe to store the round 1 district assignments
# Create the district column and initialize it to 0
michigan_counties_merged['district'] = 0

# Assign the districts to each county
# Assign the adjusted counties to districts 1 through 11 based on the solution to the adjusted model
for i in range(len(county_names_adjusted)):
    for j in range(n_districts_adjusted):
        if value(x1[(county_names_adjusted[i], j)]) == 1:
            michigan_counties_merged.loc[michigan_counties_merged['name'] == county_names_adjusted[i], 'district'] = j + 1

# Assign the northern counties to district 11
for county in northern:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district'] = 11

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    michigan_counties_merged.loc[michigan_counties_merged['name'] == large_counties[i], 'district'] = i + 12

# 6.2 Plot the districts on a map of Michigan
# Ensure that michigan_counties_merged is a GeoDataFrame
geo_michigan_adjacency_r1 = gpd.GeoDataFrame(michigan_counties_merged, geometry=gpd.GeoSeries(michigan_counties_merged['geometry']))

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
geo_michigan_adjacency_r1.plot(column='district', ax=ax, legend=True, cmap='tab20', legend_kwds={'label': "District Number"})
ax.set_title('Michigan Congressional Districts (Adjacency Constraint | Round 1)')

# Annotate each county with its assigned district number
for index, row in geo_michigan_adjacency_r1.iterrows():
    plt.annotate(text=row['district'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y), horizontalalignment='center', fontsize=6)

# Annotate each country with its name
for index, row in geo_michigan_adjacency_r1.iterrows():
    plt.annotate(text=row['name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y+.12), horizontalalignment='center', fontsize=5)

# Annotate each county with its population
for index, row in geo_michigan_adjacency_r1.iterrows():
    plt.annotate(text=row['pop2020'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y-.12), horizontalalignment='center', fontsize=5)

# Show the plot for the first round of the optimization model
plt.show()

### ----------------------------------------------------------------------------------------------------------

"""
Based on the results of this initial optimization model, we were able to identify a number of counties, specifically
in the north-west region of Michigan, that the model was indicating should be assigned to their own districts.
These counties included:
    - Leelanau
    - Benzie
    - Manistee
    - Mason
    - Wexford
    - Lake
    - GrandTraverse
    - Newaygo
    - Missaukee
    - Osceola
    - Mecosta
    - Clare
    - Kalkaska
    - Oceana
    - Crawford
    - Roscommon
    - Isabella

Additional indication of counties that should be manually assigned to their own districts based on the results of the
initial optimization model were:
    - Kent (its own district)
    - Genesee and Livingston (their own district)
"""

### ----------------------------------------------------------------------------------------------------------

# STEP 7: Create the second optimization model (Round 2)

# 7.1 Further manually assign counties to their own districts for the second round of the optimization model
# to further simply the optimization problem

# Create a list of the counties that should be in district 10
district_10 = ["Leelanau", "Benzie", "Manistee", "Mason", "Wexford", "Lake", "GrandTraverse", "Newaygo", "Missaukee", "Osceola", "Mecosta", "Clare", "Kalkaska", "Oceana", "Crawford", "Roscommon", "Isabella"]

# Create a list of the counties that should be in district 9
# This will just be Kent, given that it is above the ~564,400 ideal district population size
district_9 = ["Kent"]

# Create a list of the counties that should be in district 8
district_8 = ["Genesee", "Livingston"]

# 7.2 Created a newly updated dataframe for the second round of the optimization model and update the parameters
# Create a newly updated 'michigan_counties_adjusted' dataframe that does not include the counties that have been manually assigned
manual_counties_round2 = manual_counties + district_10 + district_9 + district_8

# Create a new datafraem that doesn't contain any of the updated manually assigned counties
michigan_counties_adjusted_round2 = michigan_counties_merged[~michigan_counties_merged['name'].isin(manual_counties_round2)]

# Adjust the number of counties and districts in Michigan
n_counties_adjusted_round2 = len(michigan_counties_adjusted_round2)
print(n_counties_adjusted_round2)
n_districts_adjusted_round2 = n_districts_adjusted - (3) # The 3 represents districts 8, 9, and 10
print(n_districts_adjusted_round2)

# Create a dictionary of the adjusted county names and their populations for the second round of manual assignments
county_populations_adjusted_round2 = michigan_counties_adjusted_round2[['name', 'pop2020']].set_index('name').to_dict()['pop2020']
county_names_adjusted_round2 = michigan_counties_adjusted_round2['name'].to_numpy()

# 7.3 Create the second optimization model
# Initialize the adjusted model for the second round of manual assignments
model2 = LpProblem("Michigan_Redistricting_Adjusted_Round2", LpMinimize)

# Decision variable: binary variable indicating whether a county is in a district
x2 = LpVariable.dicts("x_adjusted_round2", ((i, j) for i in county_names_adjusted_round2 for j in range(n_districts_adjusted_round2)), cat='Binary')

# Objective function: minimize the deviation of populations in each district from the average population
# Calculate the deviation of populations in each district from the average population
model2 += lpSum(
    ((county_populations_adjusted_round2[county_names_adjusted_round2[i]] - average_district_population_adjusted) *
     (county_populations_adjusted_round2[county_names_adjusted_round2[i]] - average_district_population_adjusted) *
     x2[(county_names_adjusted_round2[i], j)])
    for i in range(len(county_names_adjusted_round2))
    for j in range(n_districts_adjusted_round2)
)

# Constraints
# Constraints: Each county must be assigned to exactly one district
for i in range(len(county_names_adjusted_round2)):
    model2 += lpSum(x2[(county_names_adjusted_round2[i], j)] for j in range(n_districts_adjusted_round2)) == 1

# Adjacency constraint
for i in range(len(county_names_adjusted_round2)):
     for j in range(n_districts_adjusted_round2):
         model2 += lpSum(adjacency_matrix.loc[county_names_adjusted_round2[i], neighbor] * x2[(neighbor, j)] for neighbor in county_names_adjusted_round2) >= x2[(county_names_adjusted_round2[i], j)]

# The population of the district must be within 20% of the average population
for j in range(n_districts_adjusted_round2):
    model2 += lpSum(county_populations_adjusted_round2[county_names_adjusted_round2[i]] * x2[(county_names_adjusted_round2[i], j)] for i in range(len(county_names_adjusted_round2))) >= 0.80 * average_district_population_adjusted
    model2 += lpSum(county_populations_adjusted_round2[county_names_adjusted_round2[i]] * x2[(county_names_adjusted_round2[i], j)] for i in range(len(county_names_adjusted_round2))) <= 1.20 * average_district_population_adjusted

# 7.4 Solve the second optimization model
# Solve the model2
model2.solve()

# Print the status of the solution
print("Status:", LpStatus[model2.status])

# Print the objective value
print("Objective Function Value:", value(model2.objective))
print("")

# Print the district assignments along with the total district populations on a separate line starting with district 1
for j in range(n_districts_adjusted_round2):
    print("District", j + 1, ":", end = " ")
    district_population = 0
    for i in range(len(county_names_adjusted_round2)):
        if x2[(county_names_adjusted_round2[i], j)].varValue == 1:
            print(county_names_adjusted_round2[i], end = ", ")
            district_population += county_populations_adjusted_round2[county_names_adjusted_round2[i]]
    print("Total Population:", district_population)

# Manually assign the counties in district_8 to district 8 and print the population size
print("District 8:", district_8)
# print("Total Population:", sum(county_populations_adjusted_round2[county] for county in district_8))

# Manually assign the counties in district_9 to district 9 and print the population size
print("District 9:", district_9)
# print("Total Population:", sum(county_populations_adjusted_round2[county] for county in district_9))

# Manually assign the counties in district_10 to district 10 and print the population size
print("District 10:", district_10)
# print("Total Population:", sum(county_populations_adjusted_round2[county] for county in district_10))

# Manually assign the 'northern' counties in the upper peninsula to the same district (district 11), and print the population size
print("District 11:", northern)
# print("Total Population:", sum(county_populations_adjusted_round2[county] for county in northern))

# Assign the large counties to their own districts starting with district 12 and print their population sizes
for i in range(len(large_counties)):
    print("District", i + 12, ":", large_counties[i])
    # print("Total Population:", county_populations_adjusted_round2[large_counties[i]])

### ----------------------------------------------------------------------------------------------------------

# STEP 8: Visualize the generated district assignment form the second round of the optimization model to better
# understand the partitioning of districts

# 8.1 Add a column to the michigan_counties_merged dataframe to store the round 2 district assignments
# Create the district column and initialize it to 0
michigan_counties_merged['district_r2'] = 0

# Reassign the district that counties are assigned to in the 'district_assignments' column of the 'michigan_counties_merged' dataframe
# based on the solution to the second round of manual assignments
for i in range(len(county_names_adjusted_round2)):
    for j in range(n_districts_adjusted_round2):
        if value(x2[(county_names_adjusted_round2[i], j)]) == 1:
            michigan_counties_merged.loc[michigan_counties_merged['name'] == county_names_adjusted_round2[i], 'district_r2'] = j + 1

# Assign the 'district_8' counties to district 8
for county in district_8:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r2'] = 8

# Assign the 'district_9' counties to district 9
for county in district_9:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r2'] = 9

# Assign the 'district_10' counties to district 10
for county in district_10:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r2'] = 10

# Assign the 'northern' counties to district 11
for county in northern:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r2'] = 11

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    michigan_counties_merged.loc[michigan_counties_merged['name'] == large_counties[i], 'district_r2'] = i + 12

# 8.2 Plot the districts on a map of Michigan
# Ensure that michigan_counties_merged is a GeoDataFrame
geo_michigan_adjacency_r2 = gpd.GeoDataFrame(michigan_counties_merged, geometry=gpd.GeoSeries(michigan_counties_merged['geometry']))

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
geo_michigan_adjacency_r2.plot(column='district_r2', ax=ax, legend=True, cmap='tab20', legend_kwds={'label': "District Number"})
ax.set_title('Michigan Congressional Districts (Adjacency Constraint | Round 2)')

# Annotate each county with its assigned district number
for index, row in geo_michigan_adjacency_r2.iterrows():
    plt.annotate(text=row['district_r2'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y), horizontalalignment='center', fontsize=6)

# Annotate each country with its name
for index, row in geo_michigan_adjacency_r2.iterrows():
    plt.annotate(text=row['name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y+.12), horizontalalignment='center', fontsize=5)

# Annotate each county with its population
for index, row in geo_michigan_adjacency_r2.iterrows():
    plt.annotate(text=row['pop2020'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y-.12), horizontalalignment='center', fontsize=5)

# Show the plot
plt.show()

### ----------------------------------------------------------------------------------------------------------

"""
The results of the second round of manual assignments gave us further insights to guide in the third round of manual
assignments. The counties that were identified as needing to be assigned to their own districts were:
    District 7
        - Oscoda
        - Alcona
        - Ogemaw
        - Iosco
        - Gladwin
        - Arenac
        - Huron
        - Midland
        - Bay
        - Gratiot
        - Montcalm
        - Shiawassee
        - Clinton
    District 6
        - Lapeer
        - St.Clair
        - Tuscola
        - Sanilac
        - Saginaw
    District 5
        - Monroe
        - Calhoun
        - Lenawee
        - St.Joseph
        - Hillsdale
        - Branch
    District 4
        - Jackson
        - Washtenaw
    District 3
        - Ingham
        - Eaton
        - Barry
        - Ionia
"""

### ----------------------------------------------------------------------------------------------------------

# STEP 9: Create the third optimization model (Round 3)

# 9.1 Further manually assign counties to their own districts for the third round of the optimization model
# Create a list of the counties that should be in district 7
district_7 = ["Oscoda", "Alcona", "Ogemaw", "Iosco", "Gladwin", "Arenac", "Huron", "Midland", "Bay", "Gratiot", "Montcalm", "Shiawassee", "Clinton"]

# Create a list of the counties that should be in district 6
district_6 = ["Lapeer", "St.Clair", "Tuscola", "Sanilac", "Saginaw"]

# Create a list of the counties that should be in district 5
district_5 = ["Monroe", "Calhoun", "Lenawee", "St.Joseph", "Hillsdale", "Branch"]

# Create a list of the counties that should be in district 4
district_4 = ["Jackson", "Washtenaw"]

# Create a list of the counties that should be in district 3
district_3 = ["Ingham", "Eaton", "Barry", "Ionia"]

# 9.2 Created a newly updated dataframe for the third round of the optimization model and update the parameters
# Create a newly updated 'michigan_counties_adjusted' dataframe that does not include the counties that have been manually assigned
manual_counties_round3 = manual_counties_round2 + district_7 + district_6 + district_5 + district_4 + district_3

# Create a new datafraem that doesn't contain any of the updated manually assigned counties
michigan_counties_adjusted_round3 = michigan_counties_merged[~michigan_counties_merged['name'].isin(manual_counties_round3)]

# Adjust the number of counties and districts in Michigan
n_counties_adjusted_round3 = len(michigan_counties_adjusted_round3)
print(n_counties_adjusted_round3)
n_districts_adjusted_round3 = n_districts_adjusted_round2 - (5) # The 5 represents districts 3, 4, 5, 6, and 7
print(n_districts_adjusted_round3)

# Create a dictionary of the adjusted county names and their populations for the third round of manual assignments
county_populations_adjusted_round3 = michigan_counties_adjusted_round3[['name', 'pop2020']].set_index('name').to_dict()['pop2020']
county_names_adjusted_round3 = michigan_counties_adjusted_round3['name'].to_numpy()

# 9.3 Create the third optimization model
# Initialize the adjusted model for the third round of manual assignments
model3 = LpProblem("Michigan_Redistricting_Adjusted_Round3", LpMinimize)

# Decision variable: binary variable indicating whether a county is in a district
x3 = LpVariable.dicts("x_adjusted_round3", ((i, j) for i in county_names_adjusted_round3 for j in range(n_districts_adjusted_round3)), cat='Binary')

# Objective function: minimize the deviation of populations in each district from the average population
# Calculate the deviation of populations in each district from the average population
model3 += lpSum(
    ((county_populations_adjusted_round3[county_names_adjusted_round3[i]] - average_district_population_adjusted) *
     (county_populations_adjusted_round3[county_names_adjusted_round3[i]] - average_district_population_adjusted) *
     x3[(county_names_adjusted_round3[i], j)])
    for i in range(len(county_names_adjusted_round3))
    for j in range(n_districts_adjusted_round3)
)

# Constraints
# Constraints: Each county must be assigned to exactly one district
for i in range(len(county_names_adjusted_round3)):
    model3 += lpSum(x3[(county_names_adjusted_round3[i], j)] for j in range(n_districts_adjusted_round3)) == 1

# Adjacency constraint
for i in range(len(county_names_adjusted_round3)):
     for j in range(n_districts_adjusted_round3):
         model3 += lpSum(adjacency_matrix.loc[county_names_adjusted_round3[i], neighbor] * x3[(neighbor, j)] for neighbor in county_names_adjusted_round3) >= x3[(county_names_adjusted_round3[i], j)]

# The population of the district must be within 20% of the average population
for j in range(n_districts_adjusted_round3):
    model3 += lpSum(county_populations_adjusted_round3[county_names_adjusted_round3[i]] * x3[(county_names_adjusted_round3[i], j)] for i in range(len(county_names_adjusted_round3))) >= 0.80 * average_district_population_adjusted
    model3 += lpSum(county_populations_adjusted_round3[county_names_adjusted_round3[i]] * x3[(county_names_adjusted_round3[i], j)] for i in range(len(county_names_adjusted_round3))) <= 1.20 * average_district_population_adjusted

# 9.4 Solve the third optimization model
# Solve the model3
model3.solve()

# Print the status of the solution
print("Status:", LpStatus[model3.status])

# Print the objective value
print("Objective Function Value:", value(model3.objective))
print("")

# Print the district assignments along with the total district populations on a separate line starting with district 1
for j in range(n_districts_adjusted_round3):
    print("District", j + 1, ":", end = " ")
    district_population = 0
    for i in range(len(county_names_adjusted_round3)):
        if x3[(county_names_adjusted_round3[i], j)].varValue == 1:
            print(county_names_adjusted_round3[i], end = ", ")
            district_population += county_populations_adjusted_round3[county_names_adjusted_round3[i]]
    print("Total Population:", district_population)

# Manually assign the manually assigned counties to their respective districts
print("District 3:", district_3)
print("District 4:", district_4)
print("District 5:", district_5)
print("District 6:", district_6)
print("District 7:", district_7)
print("District 8:", district_8)
print("District 9:", district_9)
print("District 10:", district_10)
print("District 11:", northern)

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    print("District", i + 12, ":", large_counties[i])

### ----------------------------------------------------------------------------------------------------------

# STEP 10: Visualize the generated district assignment form the third round of the optimization model to better
# understand the partitioning of districts

# 10.1 Add a column to the michigan_counties_merged dataframe to store the round 3 district assignments
# Create the district column and initialize it to 0
michigan_counties_merged['district_r3'] = 0

# Reassign the district that counties are assigned to in the 'district_r2' column of the 'michigan_counties_merged' dataframe
# based on the solution to the third round of manual assignments
for i in range(len(county_names_adjusted_round3)):
    for j in range(n_districts_adjusted_round3):
        if value(x3[(county_names_adjusted_round3[i], j)]) == 1:
            michigan_counties_merged.loc[michigan_counties_merged['name'] == county_names_adjusted_round3[i], 'district_r3'] = j + 1

# Assign the manually assigned districts to their respective districts (districts 3 - 11)
for county in district_3:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 3
for county in district_4:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 4
for county in district_5:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 5
for county in district_6:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 6
for county in district_7:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 7
for county in district_8:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 8
for county in district_9:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 9
for county in district_10:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 10
for county in northern:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_r3'] = 11

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    michigan_counties_merged.loc[michigan_counties_merged['name'] == large_counties[i], 'district_r3'] = i + 12

# 10.2 Plot the districts on a map of Michigan
# Ensure that michigan_counties_merged is a GeoDataFrame
geo_michigan_adjacency_r3 = gpd.GeoDataFrame(michigan_counties_merged, geometry=gpd.GeoSeries(michigan_counties_merged['geometry']))

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
geo_michigan_adjacency_r3.plot(column='district_r3', ax=ax, legend=True, cmap='tab20', legend_kwds={'label': "District Number"})
ax.set_title('Michigan Congressional Districts (Adjacency Constraint | Round 3)')

# Annotate each county with its assigned district number
for index, row in geo_michigan_adjacency_r3.iterrows():
    plt.annotate(text=row['district_r3'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y), horizontalalignment='center', fontsize=6)

# Annotate each country with its name
for index, row in geo_michigan_adjacency_r3.iterrows():
    plt.annotate(text=row['name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y+.12), horizontalalignment='center', fontsize=5)

# Annotate each county with its population
for index, row in geo_michigan_adjacency_r3.iterrows():
    plt.annotate(text=row['pop2020'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y-.12), horizontalalignment='center', fontsize=5)

# Show the plot
plt.show()

### ----------------------------------------------------------------------------------------------------------

"""
Based on these results, we were easily able to identify which districts the remaining counties should be assigned to.
    District 2:
        - Ottawa
        - Muskegon
        - Allegan
    District 1:
        - Berrien
        - VanBuren
        - Kalamazoo
        - Cass
"""


### ----------------------------------------------------------------------------------------------------------
# STEP 11: Create the fourth optimization model (Round 4)

# 11.1 Further manually assign counties to their own districts for the fourth round of the optimization model
# District 2:
district_2 = ["Ottawa", "Muskegon", "Allegan"]

# District 1:
district_1 = ["Berrien", "VanBuren", "Kalamazoo", "Cass"]

# 11.2 Create a final column in the michigan_counties_merged dataframe to store the district assignments from the final round of manual assignments
# Create the district column and initialize it to 0
michigan_counties_merged['district_final'] = 0

# Assign the manually assigned districts to their respective districts, for all the districts
for county in district_1:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 1
for county in district_2:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 2
for county in district_3:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 3
for county in district_4:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 4
for county in district_5:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 5
for county in district_6:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 6
for county in district_7:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 7
for county in district_8:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 8
for county in district_9:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 9
for county in district_10:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 10
for county in northern:
    michigan_counties_merged.loc[michigan_counties_merged['name'] == county, 'district_final'] = 11

# Assign the large counties to their own districts starting with district 12
for i in range(len(large_counties)):
    michigan_counties_merged.loc[michigan_counties_merged['name'] == large_counties[i], 'district_final'] = i + 12

# 11.3 Plot the districts on a map of Michigan
# Ensure that michigan_counties_merged is a GeoDataFrame
geo_michigan_adjacency_final = gpd.GeoDataFrame(michigan_counties_merged, geometry=gpd.GeoSeries(michigan_counties_merged['geometry']))

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
geo_michigan_adjacency_final.plot(column='district_final', ax=ax, legend=True, cmap='tab20', legend_kwds={'label': "District Number"})
ax.set_title('Michigan Congressional Districts (Adjacency Constraint | Final Round)')

# Annotate each county with its assigned district number
for index, row in geo_michigan_adjacency_final.iterrows():
    plt.annotate(text=row['district_final'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y), horizontalalignment='center', fontsize=6)

# Annotate each country with its name
for index, row in geo_michigan_adjacency_final.iterrows():
    plt.annotate(text=row['name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y+.12), horizontalalignment='center', fontsize=5)

# Annotate each county with its population
for index, row in geo_michigan_adjacency_final.iterrows():
    plt.annotate(text=row['pop2020'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y-.12), horizontalalignment='center', fontsize=5)

# Show the plot
plt.show()

