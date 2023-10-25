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
file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module6/michigan_counties.xlsx'
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

### SECTION 2: READ IN SHAPEFILE FOR MAPPING

# read in shapefile
file_path = '/Users/Jai/Documents/Git_remote/Decision_analytics/Module6/michigan_counties.geojson'
shapefile_michigan = gpd.read_file(file_path)
map_population_by_county_data = shapefile_michigan.merge(michigan_counties, left_on = 'name', right_on = 'county_names', suffixes = ('_left', '_right'))

# drop unwanted columns
drop_cols = ['statefp', 'countyfp', 'countyns', 'namelsad', 'lsad', 'csafp', 'classfp', 'metdivfp', 'mtfcc', 'cbsafp', 'state_name', 'countyfp_nozero', 'count_id', 'county_names', 'aland', 'awater', 'funcstat']
map_population_by_county_data = map_population_by_county_data.drop(columns = drop_cols)

# check population df; believe that 'geometry' is what's used to create the shape of the state in gpd
map_population_by_county_data.head()

















# model variables
n_counties = 83
n_districts = 14

model = LpProblem('Compacted-Redistricting', LpMinimize) 
variable_names = [str(i) + ' ' + str(j) for j in range(1, n_districts + 1) \
                                        for i in range(1, n_counties + 1)]

variable_names.sort() 


dv_variable_y = LpVariable.matrix('Y', variable_names, cat = 'Binary')
assignment = np.array(dv_variable_y).reshape(83, 14)
dv_variable_x = LpVariable.matrix('X', variable_names, cat = 'Integer', lowBound = 0)
allocation = np.array(dv_variable_x).reshape(83, 14)

#df['count_id']



# objective function
objective_function = lpSum(assignment) 
model += objective_function

# constraints
for i in range(n_counties):
    model += lpSum(allocation[i][j] for j in range(n_districts)) == county_populations[i] , "Allocate All " + str(i)
    
