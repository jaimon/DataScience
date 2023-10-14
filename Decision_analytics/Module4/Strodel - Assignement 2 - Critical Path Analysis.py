from pulp import *

# Create a dictionary of the tasks and their durations
# Task durations are currently "dummy" data and will need to be adjusted accordingly
# Additionally, this calculate will need to be repeated for best, average, and worst case scanerios
tasks_best = {'DescribeProduct':           2, 
              'DevelopMarketing':          8, 
              'DesignBrochure':            6, 
              'RequirementsAnalysis':      6, 
              'SofwtareDesign':            8, 
              'SystemDesign':              8, 
              'Coding':                   20, 
              'WriteDocumentation':       10,
              'UnitTesting':              10,
              'SystemTesting':            12,
              'PackageDeliverables':       4,
              'SurveyPotentialMarket':    10,
              'DevelopPricingPlan':        6,
              'DevelopImplementationPlan': 8,
              'WriteClientProposal':       4}

# Create a list of the tasks
tasks_list = list(tasks_best.keys())

# Create a dictionary of the task precedences
precedences = {'DescribeProduct':           [], 
               'DevelopMarketing':          [], 
               'DesignBrochure':            ['DescribeProduct'], 
               'RequirementsAnalysis':      ['DescribeProduct'], 
               'SofwtareDesign':            ['RequirementsAnalysis'], 
               'SystemDesign':              ['RequirementsAnalysis'], 
               'Coding':                    ['SofwtareDesign', 'SystemDesign'], 
               'WriteDocumentation':        ['Coding'],
               'UnitTesting':               ['Coding'],
               'SystemTesting':             ['UnitTesting'],
               'PackageDeliverables':       ['WriteDocumentation', 'SystemTesting'],
               'SurveyPotentialMarket':     ['DevelopMarketing', 'DesignBrochure'],
               'DevelopPricingPlan':        ['PackageDeliverables', 'SurveyPotentialMarket'],
               'DevelopImplementationPlan': ['DescribeProduct', 'PackageDeliverables'],
               'WriteClientProposal':       ['DevelopPricingPlan', 'DevelopImplementationPlan']}

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {task: LpVariable(f"start_{task}", 0, None) for task in tasks_list}
end_times = {task: LpVariable(f"end_{task}", 0, None) for task in tasks_list}

# Add the constraints
for task in tasks_list:
    prob += end_times[task] == start_times[task] + tasks_best[task], f"{task}_duration"
    for predecessor in precedences[task]:
        prob += start_times[task] >= end_times[predecessor], f"{task}_predecessor_{predecessor}"

# Set the objective function        
prob += lpSum([end_times[task] for task in tasks_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for task in tasks_list:
    if value(start_times[task]) == 0:
        print(f"{task} starts at time 0")
    if value(end_times[task]) == max([value(end_times[task]) for task in tasks_list]):
        print(f"{task} ends at {value(end_times[task])} hours in duration")
        
# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)
             
# Average tasks times        
tasks_avg = {'DescribeProduct':            4, 
             'DevelopMarketing':          12, 
             'DesignBrochure':            10, 
             'RequirementsAnalysis':       8, 
             'SofwtareDesign':            12, 
             'SystemDesign':              12, 
             'Coding':                    30, 
             'WriteDocumentation':        15,
             'UnitTesting':               15,
             'SystemTesting':             18,
             'PackageDeliverables':        6,
             'SurveyPotentialMarket':     15,
             'DevelopPricingPlan':         9,
             'DevelopImplementationPlan': 12,
             'WriteClientProposal':        6}

tasks_list = list(tasks_avg.keys())

# Create a dictionary of the task precedences
precedences = {'DescribeProduct':           [], 
               'DevelopMarketing':          [], 
               'DesignBrochure':            ['DescribeProduct'], 
               'RequirementsAnalysis':      ['DescribeProduct'], 
               'SofwtareDesign':            ['RequirementsAnalysis'], 
               'SystemDesign':              ['RequirementsAnalysis'], 
               'Coding':                    ['SofwtareDesign', 'SystemDesign'], 
               'WriteDocumentation':        ['Coding'],
               'UnitTesting':               ['Coding'],
               'SystemTesting':             ['UnitTesting'],
               'PackageDeliverables':       ['WriteDocumentation', 'SystemTesting'],
               'SurveyPotentialMarket':     ['DevelopMarketing', 'DesignBrochure'],
               'DevelopPricingPlan':        ['PackageDeliverables', 'SurveyPotentialMarket'],
               'DevelopImplementationPlan': ['DescribeProduct', 'PackageDeliverables'],
               'WriteClientProposal':       ['DevelopPricingPlan', 'DevelopImplementationPlan']}

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {task: LpVariable(f"start_{task}", 0, None) for task in tasks_list}
end_times = {task: LpVariable(f"end_{task}", 0, None) for task in tasks_list}

# Add the constraints
for task in tasks_list:
    prob += end_times[task] == start_times[task] + tasks_avg[task], f"{task}_duration"
    for predecessor in precedences[task]:
        prob += start_times[task] >= end_times[predecessor], f"{task}_predecessor_{predecessor}"

# Set the objective function        
prob += lpSum([end_times[task] for task in tasks_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for task in tasks_list:
    if value(start_times[task]) == 0:
        print(f"{task} starts at time 0")
    if value(end_times[task]) == max([value(end_times[task]) for task in tasks_list]):
        print(f"{task} ends at {value(end_times[task])} hours in duration")
        
# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)
        
# Average tasks times        
tasks_worst = {'DescribeProduct':            6, 
               'DevelopMarketing':          16, 
               'DesignBrochure':            14, 
               'RequirementsAnalysis':      10, 
               'SofwtareDesign':            16, 
               'SystemDesign':              16, 
               'Coding':                    40, 
               'WriteDocumentation':        20,
               'UnitTesting':               20,
               'SystemTesting':             24,
               'PackageDeliverables':        8,
               'SurveyPotentialMarket':     20,
               'DevelopPricingPlan':        12,
               'DevelopImplementationPlan': 16,
               'WriteClientProposal':        8}

tasks_list = list(tasks_worst.keys())

# Create a dictionary of the task precedences
precedences = {'DescribeProduct':           [], 
               'DevelopMarketing':          [], 
               'DesignBrochure':            ['DescribeProduct'], 
               'RequirementsAnalysis':      ['DescribeProduct'], 
               'SofwtareDesign':            ['RequirementsAnalysis'], 
               'SystemDesign':              ['RequirementsAnalysis'], 
               'Coding':                    ['SofwtareDesign', 'SystemDesign'], 
               'WriteDocumentation':        ['Coding'],
               'UnitTesting':               ['Coding'],
               'SystemTesting':             ['UnitTesting'],
               'PackageDeliverables':       ['WriteDocumentation', 'SystemTesting'],
               'SurveyPotentialMarket':     ['DevelopMarketing', 'DesignBrochure'],
               'DevelopPricingPlan':        ['PackageDeliverables', 'SurveyPotentialMarket'],
               'DevelopImplementationPlan': ['DescribeProduct', 'PackageDeliverables'],
               'WriteClientProposal':       ['DevelopPricingPlan', 'DevelopImplementationPlan']}

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {task: LpVariable(f"start_{task}", 0, None) for task in tasks_list}
end_times = {task: LpVariable(f"end_{task}", 0, None) for task in tasks_list}

# Add the constraints
for task in tasks_list:
    prob += end_times[task] == start_times[task] + tasks_worst[task], f"{task}_duration"
    for predecessor in precedences[task]:
        prob += start_times[task] >= end_times[predecessor], f"{task}_predecessor_{predecessor}"

# Set the objective function        
prob += lpSum([end_times[task] for task in tasks_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for task in tasks_list:
    if value(start_times[task]) == 0:
        print(f"{task} starts at time 0")
    if value(end_times[task]) == max([value(end_times[task]) for task in tasks_list]):
        print(f"{task} ends at {value(end_times[task])} hours in duration")
        
# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)
        
print('Test git update commit')