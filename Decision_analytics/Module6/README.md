# Redistricting Michigan's Congressional Districts Using Integer Programming

## Overview
This project focuses on devising an optimal solution for redistricting Michigan's congressional districts using integer programming techniques. This repository contains the Python scripts we developed to tackle this optimization problem, as well as the data sets that were integral to our solution.

## Data Sets
Here's a brief description of the data files used in this project, along with their sources:

- **Michigan Counties (Excel)**: 
    - **Description**: Contains a list of all Michigan counties, their populations, and central coordinates (longitude/latitude).
    
- **Michigan Counties (GeoJSON)**:
    - **Description**: Provides geographical details for Michigan counties.
    
- **County Adjacency (txt)**:
    - **Description**: Contains information on county adjacencies for all U.S. counties. For our project, we extracted data pertinent to Michigan. This was essential to develop the adjacency matrix utilized in our optimization model's adjacency constraint.

- **Sources**:
    - [Population Data](https://www.michigan-demographics.com/counties_by_population)
    - [Geopoints & Shapefile Data](https://public.opendatasoft.com/explore/dataset/us-county-boundaries/export/?flg=en-us&disjunctive.statefp&disjunctive.countyfp&disjunctive.name&disjunctive.namelsad&disjunctive.stusab&disjunctive.state_name&sort=stusab&refine.statefp=26)
    - [County Adjacency Data](https://www2.census.gov/geo/docs/reference/county_adjacency.txt)

> **Note**: Files used in this model are appended with a "mod" label, indicating that two-word county names have been merged into single words. This simplification facilitates data handling, especially for the adjacency matrix.

## Model Approach
Our model primarily employed a combination of optimization and manual adjustments:

1. **Manual Adjustments**:
   - Counties were manually assigned to districts.
   - This reduced decision variables for optimization, thereby streamlining the problem.
   - With each manual iteration, the model refined its solutions, guiding subsequent manual adjustments.

2. **Why This Approach?**:
   - We faced challenges in developing a contiguous constraint that mandated all counties within a district to be interconnected. The combination approach helped us bypass this constraint.

### Model Details:
- **Objective Function**: Minimize the population deviation in each district from the average ("ideal") population.
  
- **Decision Variables**: Binary variable indicating county presence in a district.
  
- **Constraints**:
    1. Every county must belong to one and only one district.
    2. A county in a district should share borders with at least another county in the same district.
    3. District populations should be within 20% of the ideal population.