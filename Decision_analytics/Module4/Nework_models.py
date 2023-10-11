# Critical Path Analysis 

# Problem description from Williams (2013, pages 95-98)
# Williams, H. Paul. 2013. Model Building in Mathematical Programming (fifth edition). New York: Wiley. [ISBN-13: 978-1-118-44333-0]

# Python PuLP solution prepared by Thomas W. Miller
# Revised April 20, 2023
# Implemented using activities dictionary with derived start_times and end_times
# rather than time decision variables as in Williams (2013)

from pulp import *

# Create a dictionary of the activities and their durations
activities = {'DigFoundations':4, 'LayFoundations':2, 'ObtainBricks':7, 'ObtainTiles':12, 'Walls':10, 'Roofing':5, 'Wiring':3, 'Painting':4}

# Create a list of the activities
activities_list = list(activities.keys())

# Create a dictionary of the activity precedences
precedences = {'DigFoundations': [], 'ObtainBricks': [], 'ObtainTiles': [], 'LayFoundations': ['DigFoundations'],  'Walls': ['DigFoundations','ObtainBricks'], 'Wiring': ['Walls'], 'Roofing': ['ObtainTiles','Walls'], 'Painting': ['Wiring','Roofing']}

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list}

# Add the constraints
for activity in activities_list:
    prob += end_times[activity] == start_times[activity] + activities[activity], f"{activity}_duration"
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"

# Set the objective function
prob += lpSum([end_times[activity] for activity in activities_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for activity in activities_list:
    if value(start_times[activity]) == 0:
        print(f"{activity} starts at time 0")
    if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list]):
        print(f"{activity} ends at {value(end_times[activity])} days in duration")

# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)

