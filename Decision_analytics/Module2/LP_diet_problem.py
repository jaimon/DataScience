# %%
# import pulp
from pulp import LpVariable, LpProblem, LpMaximize, LpStatus, value, LpMinimize
import pulp


# %%
problem = pulp.LpProblem("Minimum Cost Diet", pulp.LpMinimize)

# Define the decision variables
x1 = pulp.LpVariable(name="Almonds",lowBound=0) #Almonds
x2 = pulp.LpVariable(name="Chicken",lowBound=0) #Chicken
x3 = pulp.LpVariable(name="Spinach",lowBound=0) #Spinach
x4 = pulp.LpVariable(name="Quinoa",lowBound=0) #Quinoa
x5 = pulp.LpVariable(name="Salmon",lowBound=0) #Salmon

# %%
# Define the constraints
problem += 0 * x1 + 90 * x2 + 65 * x3 + 0 * x4 + 80 * x5 <= 5000 # Sodium
problem += 170 * x1 + 250 * x2 + 20 * x3 + 170 * x4 + 160 * x5 >= 2000 # Energy
problem += 7 * x1 + 19 * x2 + 2 * x3 + 6 * x4 + 23 * x5 >= 50 # Protein
problem += 0 * x1 + 8 * x2 + 65 * x3 + 0 * x4 + 80 * x5 >= 20 # Vitamin D
problem += 80 * x1 + 9 * x2 + 80 * x3 + 20 * x4 + 0 * x5 >= 1300 # Calcium
problem += 1 * x1 + 0.8 * x2 + 2.3 * x3 + 2.1 * x4 + 0.72 * x5 >= 18 # Iron
problem += 220 * x1 + 230 * x2 + 470 * x3 + 250 * x4 + 376 * x5 >= 4700 # Potassium

# %%
# Define the objective function

problem +=  0.75 * x1 + 1.032 * x2 + 1.145 * x3 + 0.5482 * x4 + 3.49 * x5

# %%
# Solve the Problem
problem.solve()

# Output the results
if pulp.LpStatus[problem.status] == 'Optimal':
    print(f"Number of servings of Almonds: {x1.value()}")
    print(f"Number of servings of Chicken: {x2.value()}")
    print(f"Number of servings of Spinach: {x3.value()}")
    print(f"Number of servings of Quinoa: {x4.value()}")
    print(f"Number of servings of Salmon: {x5.value()}")
    print(f"Total Cost of Diet: ${pulp.value(problem.objective)}")
else:

    print("No optimal solution found.")

# %%


problem2 = pulp.LpProblem("Minimum Cost Diet", pulp.LpMinimize)

# Define the decision variables
#x1 = pulp.LpVariable(name="Almonds",lowBound=0) #Almonds
x2 = pulp.LpVariable(name="Chicken",lowBound=0) #Chicken
x3 = pulp.LpVariable(name="Spinach",lowBound=0) #Spinach
x4 = pulp.LpVariable(name="Quinoa",lowBound=0) #Quinoa
x5 = pulp.LpVariable(name="Salmon",lowBound=0) #Salmon


#Add additional food items
x6 = pulp.LpVariable(name="Rice",lowBound=0) #Rice
x7 = pulp.LpVariable(name="Waffles",lowBound=0) #Waffles
x8 = pulp.LpVariable(name="Yogurt",lowBound=0) #Yogurt
x9 = pulp.LpVariable(name="Bread",lowBound=0)  #Bread


#Add additional nutrients(Vitamin A and Vitamin C) to the constraints to see if it changes the total cost

problem2 +=  90 * x2 + 65 * x3 + 0 * x4 + 80 * x5 + 0 * x6 + 390 * x7 + 75 * x8 + 170 * x9 <= 5000 # Sodium
problem2 +=  250 * x2 + 20 * x3 + 170 * x4 + 160 * x5 + 170 * x6 + 250 * x7 + 140 * x8 + 130 * x9 >= 2000 # Energy
problem2 +=  19 * x2 + 2 * x3 + 6 * x4 + 23 * x5 + 3 * x6 + 12 * x7 + 10 * x8 + 6 * x9 >= 50 # Protein
problem2 +=  8 * x2 + 65 * x3 + 0 * x4 + 80 * x5 + 0 * x6 + 0 * x7 + 0 * x8 + 0 * x9 >= 20 # Vitamin D
problem2 +=  9 * x2 + 80 * x3 + 20 * x4 + 0 * x5 + 10 * x6 + 50 * x7 + 0.1 * x8 + 30 * x9 >= 1300 # Calcium
problem2 +=  0.8 * x2 + 2.3 * x3 + 2.3 * x3 + 2.1 * x4 + 0.72 * x5 + 0.4 * x6 + 1.4 * x7 + 0 * x8 + 1.3 * x9 >= 18 # Iron
problem2 +=  230 * x2 + 470 * x3 + 376 * x5 + 50 * x6 + 130 * x7 + 0.04 * x8 + 40 * x9 >= 4700 # Potassium
problem2 +=  0 * x2 + 0 * x3 + 0 * x4 + 58.10 * x5 + 0 * x6 + 0 * x7 + 0 * x8 + 0 * x9 >= 900 #Vitamin A
problem2 +=  0 * x2 + 0 * x3 + 0 * x4 + 7.7 * x5 + 0 * x6 + 0 * x7 + 0 * x8 + 0 * x9 >= 90 #Vitamin C

# %%
# Define the objective function after adding new food items and additional nutrients

problem2 +=  1.032 * x2 + 1.145 * x3 +  0.5482 * x4  + 3.49 * x5 + 0.845 * x6 + 1.484 * x7 + 1.14 * x8 + 0.28 * x9

# %%
# Solve the Problem
problem2.solve()

# Output the results
if pulp.LpStatus[problem.status] == 'Optimal':
    print(f"Number of servings of Chicken: {x2.value()}")
    print(f"Number of servings of Spinach: {x3.value()}")
    print(f"Number of servings of Quinoa: {x4.value()}")
    print(f"Number of servings of Salmon: {x5.value()}")
    print(f"Number of servings of Rice: {x6.value()}")
    print(f"Number of servings of Waffles: {x7.value()}")
    print(f"Number of servings of Yogurt: {x8.value()}")
    print(f"Number of servings of Bread: {x9.value()}")
    
    print(f"Total Cost of Diet: ${pulp.value(problem2.objective)}")
else:
    print("No optimal solution found.")


