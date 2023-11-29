# %%
"""
Import the required libraries
"""
import simpy
import random
import statistics
import os
import logging
import csv

# %%
"""
Set up the logging for the simulation 
"""
logging.basicConfig(filename='er_trace_output.txt', filemode='w',level=logging.INFO, format='%(message)s') # Set up logging
logger = logging.getLogger() # Get logging object

def log_event(message): # Function to log events
    logger.info(message) # Log the event

# %%
"""
Set up the CSV file for the simulation
"""

def write_event_to_csv(event_data, filename='er_event_log.csv', mode='a'): # Function to write events to CSV file
    with open(filename, mode, newline='') as file: # Open CSV file in append mode
        writer = csv.writer(file) # Create CSV writer object
        if mode == 'w': # If write mode, write headers
            writer.writerow(['Event_Type', 'Patient_ID', 'Time'])  # Write headers if in write mode
        writer.writerow(event_data) # Write event data to CSV file
# %%
"""
Set up the ER class
The ER class has the following attributes:
    1. env: The simpy environment
    2. reception: The reception resource
    3. nurses: The nurses resource
    4. doctors: The doctors resource
    5. trauma_rooms: The trauma rooms resource
    6. exam_rooms: The exam rooms resource
"""
wait_times = [] # Create an empty list to store wait times

class ER(object): # The clas to represent the Emnergency Room
    def __init__(self, env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms): # Initialize the class
        self.env = env # Set the simpy environment
        self.reception = simpy.Resource(env, num_reception) # Create the reception resource
        self.nurses = simpy.Resource(env, num_nurses) # Create the nurses resouce
        self.doctors = simpy.Resource(env, num_doctors) # Create the doctors resource
        self.trauma_rooms = simpy.Resource(env, num_trauma_rooms) # Create the trauma rooms resource
        self.exam_rooms = simpy.Resource(env, num_exam_rooms) # Create the exam rooms resource
    """
    Create the methods for the ER class
    The methods are the service times for each of the resources
    The methods are called by the go_to_er function
    The go_to_er function is called by the run_er function
    The run_er function is called by the main function
    The main function is called by the if __name__ == '__main__' statement at the end of the file
    """
    
    """
    We want to make an adjustment to the randomization of service times so that they follow an exponential distribution
    to better model the variability seen in real-world ERs
    """
    # Arrival time
    def arrival(self, patient): # The arrival method
        yield self.env.timeout(random.expovariate(1 / 10)) # The arrival time is exponentially distributed with a mean of 10 minutes
        event_data = ['Arrival', patient, self.env.now]
        
    # Service time for reception
    def reception(self, patient): # The reception method
        yield self.env.timeout(random.expovariate(1 / 10)) # The service time is exponentially distributed with a mean of 10 minutes
        event_data = ['Reception', patient, self.env.now]
        
#service times
    def triage(self, patient):
        yield self.env.timeout(random.randint(1, 10))
        event_data = ['Triage', patient, self.env.now]
        #log_event(f"Patient {patient} received by Triage at time {self.env.now}")
        #write_event_to_csv(event_data)

#service times
    def exam_room(self, patient):
        yield self.env.timeout(random.randint(1, 10))
        event_data = ['Exam_room', patient, self.env.now]
        #log_event(f"Patient {patient} received in Exam room at time {self.env.now}")
        #write_event_to_csv(event_data)

#service times
    def trauma_room(self, patient):
        yield self.env.timeout(random.randint(1, 10))
        event_data = ['Trauma_room', patient, self.env.now]
        #log_event(f"Patient {patient} received in Trauma room at time {self.env.now}")
        #write_event_to_csv(event_data)
        


# %%
def go_to_er(env, patient, er_instance):
    arrival_time = env.now
    log_event(f"Patient {patient} arrived in ER at time {arrival_time}")
    write_event_to_csv(['Patient_Arrival', patient, arrival_time])

    with er_instance.reception.request() as request:
        yield request
        reception_start_time = env.now
        log_event(f"Patient {patient} arrived in reception at time {reception_start_time}")
        write_event_to_csv(['Reception_Start_time', patient, reception_start_time])
        yield env.process(er_instance.arrival(patient))
        reception_end_time = env.now
        log_event(f"Patient {patient} left reception at time {reception_end_time}")
        write_event_to_csv(['Reception_End_time', patient, reception_end_time])
        # New code to calculate the wait time for reception
        reception_waiting_time = reception_start_time - arrival_time
        log_event(f"Patient {patient} waited {reception_waiting_time} minutes for reception")
        write_event_to_csv(['Reception_Waiting_time', patient, reception_waiting_time])

    with er_instance.nurses.request() as request:
        yield request
        triage_start_time = env.now
        log_event(f"Patient {patient} received by Triage at time {triage_start_time}")
        write_event_to_csv(['Triage_Start_time', patient, triage_start_time])
        yield env.process(er_instance.triage(patient))
        triage_end_time = env.now
        log_event(f"Patient {patient} completed Triage at time {triage_end_time}")
        write_event_to_csv(['Triage_End_time', patient, triage_end_time])
        # New code to calculate the wait time for triage
        triage_waiting_time = triage_start_time - reception_end_time
        log_event(f"Patient {patient} waited {triage_waiting_time} minutes for triage")
        write_event_to_csv(['Triage_Waiting_time', patient, triage_waiting_time])

    if random.choice([True, False]):
        with er_instance.doctors.request() as request:
            yield request
            trauma_start_time = env.now
            log_event(f"Patient {patient} arrived in Trauma room at time {trauma_start_time}")
            write_event_to_csv(['Trauma_Room_Service_Start_time', patient, trauma_start_time])
            yield env.process(er_instance.trauma_room(patient))
            trauma_end_time = env.now
            log_event(f"Patient {patient} left Trauma room at time {trauma_end_time}")
            write_event_to_csv(['Trauma_Room_Service_End_time', patient, trauma_end_time])
            # New code to calculate the time spent in trauma room
            trauma_room_duration = trauma_end_time - trauma_start_time
            log_event(f"Patient {patient} spent {trauma_room_duration} minutes in trauma room")
            write_event_to_csv(['Trauma_Room_Service_Duration', patient, trauma_room_duration])


    wait_times.append(env.now - arrival_time)
    departure_time = env.now
    log_event(f"Patient {patient} left the ER at time {departure_time}")
    write_event_to_csv(['Patient_Departure', patient, departure_time])

# %%
def run_er(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms):
    er_instance = ER(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms)
    log_event("ER simulation run starts")
    for patient in range(3):
        env.process(go_to_er(env, patient, er_instance))

    while True:
        yield env.timeout(10)  # Wait a bit before generating a new patient 

        patient += 1
        env.process(go_to_er(env, patient, er_instance))

# %%
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


# %%
def get_user_input():
    num_reception = int(input("Input # of receptionists working: "))
    num_nurses = int(input("Input # of nurses working: "))
    num_doctors = int(input("Input # of doctors working: "))
    num_trauma_rooms = int(input("Input # of trauma rooms: "))
    num_exam_rooms = int(input("Input # of exam rooms: "))
    return num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms


# %%
def main():
    # Reset the CSV file at the start
    write_event_to_csv([], mode='w')
    random.seed(42)
    num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms = get_user_input()

    total_simulation_runs = 50
    average_waiting_times = []
    log_event("Simulation starts")
    for _ in range(total_simulation_runs):
        wait_times.clear()  # Reset wait times for each simulation run
        env = simpy.Environment()
        env.process(run_er(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms))
        env.run(until=90)

        mins, secs = get_average_wait_time(wait_times)
        average_waiting_times.append(mins * 60 + secs)
    log_event("Simulation ends")
    total_average_waiting_time = sum(average_waiting_times) / total_simulation_runs

    if total_average_waiting_time < 60:
        print("Goal achieved! The total average time in the ER is less than one hour.")
    else:
        print("Goal not achieved. The total average time in the ER is one hour or more.")

    print("The total average waiting time across {} runs is {:.2f} minutes.".format(total_simulation_runs, total_average_waiting_time))

if __name__ == "__main__":
    main()