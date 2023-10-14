# %%
from pulp import *

# Create a LP minimization problem
model = LpProblem("Project planning", LpMinimize)


# %%
# Define workers and their hourly rates
workers = {
    'ProjectManager': 72,  # Example hourly rate for the project manager
    'FrontendDeveloper': 60,
    'BackendDeveloper': 60,
    'DataScientist': 58,
    'DataEngineer': 72,
}

# %%
# Define tasks and their estimated times for different scenarios
activities = {
    'Describe product': {'ExpectedTime': 4},
    'Develop marketing strategy': {'ExpectedTime': 12},
    'Design brochure': {'ExpectedTime': 10},
    'Develop product protoype': {'ExpectedTime': 60},
    'Requirements analysis': {'ExpectedTime': 8},
    'Software design': {'ExpectedTime': 12},
    'System design':{'ExpectedTime': 12}, 
    'Coding': {'ExpectedTime': 30},
    'Write documentation': {'ExpectedTime': 15},
    'Unit testing': {'ExpectedTime': 15},
    'System testing': {'ExpectedTime': 18},
    'Package deliverables': {'ExpectedTime': 6},
    'Survey potential market': {'ExpectedTime': 15},
    'Develop pricing plan': {'ExpectedTime': 9},
    'Develop implementation  plan': {'ExpectedTime': 12},
    'Write client proposal': {'ExpectedTime': 6}
}


# %%
# Create a list of the activities
activities_list = list(activities.keys())


# %%
# Create a dictionary of the activity precedences
precedences = {
            'Describe product': [],
            'Develop marketing strategy': [], 
            'Design brochure': ['Describe product'], 
            'Develop product protoype': [],  
            'Requirements analysis': ['Describe product'], 
            'Software design': ['Requirements analysis'], 
            'System design': ['Requirements analysis'], 
            'Coding': ['Software design','System design'],
            'Write documentation': ['Coding'],
            'Unit testing': ['Coding'],
            'System testing' : ['Unit testing'],
            'Package deliverables': ['Write documentation','System testing'],
            'Survey potential market':['Develop marketing strategy','Design brochure'],
            'Develop pricing plan': ['Package deliverables','Survey potential market'],
            'Develop implementation  plan': ['Describe product','Package deliverables'],
            'Write client proposal': ['Develop pricing plan','Develop implementation  plan']
            }


# %%
# Define decision variables
x = pulp.LpVariable.dicts("Hours", [(worker, task) for worker in workers for task in activities],
                           lowBound=0)


# %%
#Objective function
model += pulp.lpSum(x[(worker, task)] * activities[task]['ExpectedTime'] for worker in workers for task in activities)

# %%
#Constraints
for task in activities:
    model += pulp.lpSum(x[(worker, task)] for worker in workers) >= activities[task]['ExpectedTime']

# Ensure that workers are available
# Example: Assuming 160 hours of work per worker
for worker in workers:
    model += pulp.lpSum(x[(worker, task)] for task in activities) <= 160


# %%
# Solve the linear programming problem
model.solve()

# Print the results
for worker in workers:
    for task in activities:
        if x[(worker, task)].varValue > 0:
            print(f"{worker} works {x[(worker, task)].varValue} hours on {task}")

print(f"Total Expected time: {pulp.value(model.objective)}")


# %%
# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)


# %%
# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list}


# %%
# Add the constraints
for activity in activities_list:
    prob += end_times[activity] == start_times[activity] + activities[activity], f"{activity}_duration"
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"


# %%
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


