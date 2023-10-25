# data sources:
# populations https://www.michigan-demographics.com/counties_by_population
# geopoints https://public.opendatasoft.com/explore/dataset/us-county-boundaries/export/?flg=en-us&disjunctive.statefp&disjunctive.countyfp&disjunctive.name&disjunctive.namelsad&disjunctive.stusab&disjunctive.state_name&sort=stusab
# shapefile https://public.opendatasoft.com/explore/dataset/us-county-boundaries/export/?flg=en-us&disjunctive.statefp&disjunctive.countyfp&disjunctive.name&disjunctive.namelsad&disjunctive.stusab&disjunctive.state_name&sort=stusab&refine.statefp=26

# import libraries
import numpy as np
import geopandas as gpd   
import pandas as pd 
from math import pi, pow, sin, cos, asin, sqrt, floor
from pulp import *

### SECTION 1: CALCULATE DISTANCES BETWEEN COUNTY PAIRS

# define Dr. Miller functions to calculate distance between two sets of longitudes / latitudes
def degrees_to_radians(x):
     return((pi / 180) * x)

def lon_lat_distance_miles(lon_a, lat_a, lon_b, lat_b):
    radius_of_earth = 24872 / (2 * pi)
    c = sin((degrees_to_radians(lat_a) - \
    degrees_to_radians(lat_b)) / 2)**2 + \
    cos(degrees_to_radians(lat_a)) * \
    cos(degrees_to_radians(lat_b)) * \
    sin((degrees_to_radians(lon_a) - \
    degrees_to_radians(lon_b))/2)**2
    return(2 * radius_of_earth * (asin(sqrt(c))))    

def lon_lat_distance_meters (lon_a, lat_a, lon_b, lat_b):
    return(lon_lat_distance_miles(lon_a, lat_a, lon_b, lat_b) * 1609.34)

# read in file with county id, county names, latitudes, longitudes, and populations
file_path = '/Users/forreststrodel/Desktop/Northwestern/MSDS 460/Assignments/Assignment 3/michigan_counties.xlsx'
michigan_counties = pd.read_excel(file_path, index_col = None)

# remove population to allow easy joining of long and lat for each county pair
lat_lon = ['county_names', 'latitude', 'longitude']
lat_lon = michigan_counties[lat_lon]

# create list of county names for pairing        
county_names = michigan_counties['county_names'].to_numpy()

# create each unique pair
pairs = []

for i in range(len(county_names)):
    for j in range(i + 1, len(county_names)):
        pairs.append((county_names[i], county_names[j]))

col_names = ['county_1', 'county_2']
                
county_pairs = pd.DataFrame(pairs, columns = col_names)

# add first county longitude and latitdue
county_pairs = county_pairs.merge(lat_lon, left_on = 'county_1', right_on = 'county_names', how = 'left')
county_pairs.drop('county_names', axis = 1, inplace = True)
county_pairs = county_pairs.rename(columns={'latitude': 'county_1_lat', 'longitude': 'county_1_long'})

# add second county longitude and latitude
county_pairs = county_pairs.merge(lat_lon, left_on = 'county_2', right_on = 'county_names', how = 'left')
county_pairs.drop('county_names', axis = 1, inplace = True)
county_pairs = county_pairs.rename(columns={'latitude': 'county_2_lat', 'longitude': 'county_2_long'})

# add distance between each county pair in miles and meters;
distance_miles = []
distance_meters = []

for i in range(len(county_pairs)):
    distance_miles.append(lon_lat_distance_miles(county_pairs.iloc[i, 2], county_pairs.iloc[i, 3], county_pairs.iloc[i, 4], county_pairs.iloc[i, 5]))
    distance_meters.append(lon_lat_distance_meters(county_pairs.iloc[i, 2], county_pairs.iloc[i, 3], county_pairs.iloc[i, 4], county_pairs.iloc[i, 5]))

county_pairs['distance_miles'] = distance_miles
county_pairs['distance_meters'] = distance_meters

# check table
county_pairs.head()
county_pairs.tail()

county_populations = np.array(map_population_by_county_data['pop2020'])

### SECTION 2: READ IN SHAPEFILE FOR MAPPING

# read in shapefile
file_path = '/Users/forreststrodel/Desktop/Northwestern/MSDS 460/Assignments/Assignment 3/michigan_counties.geojson'
shapefile_michigan = gpd.read_file(file_path)
map_population_by_county_data = shapefile_michigan.merge(michigan_counties, left_on = 'name', right_on = 'county_names', suffixes = ('_left', '_right'))

# drop unwanted columns
drop_cols = ['statefp', 'countyfp', 'countyns', 'namelsad', 'lsad', 'csafp', 'classfp', 'metdivfp', 'mtfcc', 'cbsafp', 'state_name', 'countyfp_nozero', 'count_id', 'county_names', 'aland', 'awater', 'funcstat']
map_population_by_county_data = map_population_by_county_data.drop(columns = drop_cols)

# check population df; believe that 'geometry' is what's used to create the shape of the state in gpd
map_population_by_county_data.head()

# SECTION 3: IDENTIFY ADJACENT COUNTIES

# Determine adjacency between counties based on their geometries
adjacency_matrix = []

# Loop through each county in the GeoJSON file and determine its adjacency to all other counties
for index_1, county_1 in map_population_by_county_data.iterrows(): # Loop through each county in the GeoJSON file
    neighbors = [] # Create an empty list to store the names of neighboring counties
    for index_2, county_2 in map_population_by_county_data.iterrows(): # Loop through each county in the GeoJSON file
        # Check if the two counties are the same to avoid self-comparison
        if county_1['name'] != county_2['name']:
            if county_1['geometry'].touches(county_2['geometry']): # Check if the two counties touch
                neighbors.append(county_2['name']) # If they do, add the name of the second county to the list of neighbors
    adjacency_matrix.append(neighbors) # Add the list of neighbors to the adjacency matrix

# Add adjacency information to the dataframe
map_population_by_county_data['adjacent_counties'] = adjacency_matrix

# Check the adjacency information for the first few counties
map_population_by_county_data[['name', 'adjacent_counties']].head()

# SECTION 3: DEFINE THE INTEGER PROGRAMMING PROBLEM

# constants
n_counties = len(county_pairs['county_1'].unique())
n_districts = 14
districts = list(range(1, n_districts + 1))
population_tolerance = 0.20
total_state_population = map_population_by_county_data['pop2020'].sum()

# create binary decision variables
x = LpVariable.dicts('x', [(i, j) for i in range(n_counties) for j in range(n_districts)], cat = LpBinary)

# create the PuLP model
model = LpProblem("County_District_Assignment", LpMinimize)

# define the objective function
for i in range(n_counties):
    for j in range(n_districts):
        distance = 0
        matching_rows = county_pairs[(county_pairs['county_1'] == county_names[i]) & (county_pairs['county_2'] == county_names[j])]
        if not matching_rows.empty: # need this constraint because there is no pair for county 1 = county 1 or county 2 = county 2
            distance = matching_rows['distance_miles'].values[0]
        model += distance * x[i, j]

# add constraint that each county must be assigned to one district
for i in range(n_counties):
    model += lpSum(x[i, j] for j in range(n_districts)) == 1
    
# TO DO: Add constraint that says each district should be ~20% =/- total state popultion
county_population = {county: map_population_by_county_data[map_population_by_county_data['name'] == county]['pop2020'].values[0] for county in county_names}

district_population = []

for j in range(n_districts):
    district_population.append(value(lpSum(x[i, j] * county_population[county_names[i]] for i in range(n_counties))))

for j in range(n_districts):
    # Create a LpConstraintVar for the lower bound
    lower_bound = (1 - population_tolerance) * total_state_population
    lower_bound_constraint = LpConstraint(e=lower_bound, sense = LpConstraintLE, name=f'Lower_Bound_District_{j}')

    # Create a LpConstraintVar for the upper bound
    upper_bound = (1 + population_tolerance) * total_state_population
    upper_bound_constraint = LpConstraint(e=upper_bound, sense=LpConstraintGE, name=f'Upper_Bound_District_{j}')

    # Add the constraints to the model
    model += lower_bound_constraint
    model += upper_bound_constraint

# solve the model
model.solve()

# create an assignment to see what counties are assigned to what districts
# 'assignments' contains 1 if a county is assigned to a district, and 0 otherwise
assignments = {}

for i in range(n_counties):
    for j in range(n_districts):
        assignments[(county_names[i], str(districts[j]))] = x[i, j].varValue

# print the results for each county and sitrict
for (county, district), assignment in assignments.items():
    if assignment == 1:
        #print(f'{county} is assigned to district {district}')
        print({district})