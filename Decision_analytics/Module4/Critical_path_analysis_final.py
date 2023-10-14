# Create a list of tasks
from pulp import *

# Create a dictionary for best, average, and worst task times, respectively
tasks = {'DescribeProduct':           [ 2,  4,  6],
         'DevelopMarketing':          [ 8, 12, 16],
         'DesignBrochure':            [ 6, 10, 14],
         'RequirementsAnalysis':      [ 6,  8, 10],
         'SofwtareDesign':            [ 8, 12, 16],
         'SystemDesign':              [ 8, 12, 16],
         'Coding':                    [20, 30, 40],
         'WriteDocumentation':        [10, 15, 20],
         'UnitTesting':               [10, 15, 20],
         'SystemTesting':             [12, 18, 24],
         'PackageDeliverables':       [ 4,  6,  8],
         'SurveyPotentialMarket':     [10, 15, 20],
         'DevelopPricingPlan':        [ 6,  9, 12],
         'DevelopImplementationPlan': [ 8, 12, 16],
         'WriteClientProposal':       [ 4,  6,  8]}
tasks_list = list(tasks.keys())

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

def solvelp(i):
# Create the LP problem
    prob = LpProblem("Critical Path", LpMinimize)

    # Create the LP variables
    start_times = {task: LpVariable(f"start_{task}", 0, None) for task in tasks_list}
    end_times = {task: LpVariable(f"end_{task}", 0, None) for task in tasks_list}

    # Add the constraints
    for task in tasks_list:
        prob += end_times[task] == start_times[task] + tasks[task][i], f"{task}_duration"
        for predecessor in precedences[task]:
            prob += start_times[task] >= end_times[predecessor], f"{task}_predecessor_{predecessor}"

    # Set the objective function        
    prob += lpSum([end_times[task] for task in tasks_list]), "minimize_end_times"

    # Solve the LP problem
    status = prob.solve()

    # Print the results
    print('Critical Path Time:')
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

solvelp(0)
solvelp(1)
solvelp(2)