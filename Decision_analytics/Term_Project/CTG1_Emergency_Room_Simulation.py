# %%
import simpy
import random
import statistics
import os
import numpy as np


# %%
import logging

# Setup logging

logging.basicConfig(filename='er_trace_output.txt', filemode='w',level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def log_event(message):
    logger.info(message)

# %%
import csv

def write_event_to_csv(event_data, filename='er_event_log.csv', mode='a'):
    with open(filename, mode, newline='') as file:
        writer = csv.writer(file)
        if mode == 'w':
            writer.writerow(['Event_Type', 'Patient_ID', 'Time'])  # Write headers if in write mode
        writer.writerow(event_data)


# %%1
1
wait_times = []

class ER(object):
    def __init__(self, env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms, num_imaging_rooms):
        self.env = env
        self.reception = simpy.Resource(env, num_reception)
        self.nurses = simpy.Resource(env, num_nurses)
        self.doctors = simpy.Resource(env, num_doctors)
        self.trauma_rooms = simpy.Resource(env, num_trauma_rooms)
        self.exam_rooms = simpy.Resource(env, num_exam_rooms)
        self.imaging_rooms = simpy.Resource(env, num_imaging_rooms)
        self.consultation = simpy.Resource(env, num_doctors)  # Assuming doctors do the consultation

# Try to make these service times more realistic

#service times
    def arrival(self, patient):
        # Normal distribution with mean 5 minutes and standard deviation 2
        service_time = np.random.exponential(1010)
        yield self.env.timeout(service_time)
        event_data = ['Arrival', patient, self.env.now]


#service times
    def triage(self, patient):
         # Exponential distribution with mean 10 minutes
        service_time = np.random.exponential(15)
        yield self.env.timeout(service_time)
        event_data = ['Triage', patient, self.env.now]

#service times
    def exam_room(self, patient):
        # Normal distribution with mean 15 minutes and standard deviation 5
        service_time = np.random.exponential(30)
        yield self.env.timeout(service_time)
        event_data = ['Exam_room', patient, self.env.now]


#service times
    def trauma_room(self, patient):
        # Normal distribution with mean 20 minutes and standard deviation 7
        service_time = np.random.exponential(45)
        yield self.env.timeout(service_time)
        event_data = ['Trauma_room', patient, self.env.now]


#service times
    def imaging(self, patient):
        # Exponential distribution with mean 15 minutes
        service_time = np.random.exponential(15)
        yield self.env.timeout(service_time)

#service times         
    def doctor_consultation(self, patient):
        service_time = np.random.exponential(12)
        yield self.env.timeout(service_time)

# %%
def go_to_er(env, patient, er_instance):
    arrival_time = env.now
    log_event(f"Patient {patient} arrived in ER at time {arrival_time}")
    write_event_to_csv(['Patient_Arrival', patient, arrival_time])

     # New logic to determine if a patient needs immediate care
    needs_immediate_care = random.choice([True, False])  # Example condition

    if needs_immediate_care:
         with er_instance.doctors.request() as request:
            yield request
            trauma_start_time = env.now
            log_event(f"Patient {patient} arrived in Trauma room at time {trauma_start_time}")
            write_event_to_csv(['Trauma_Room_Service_Start_time', patient, trauma_start_time])
            yield env.process(er_instance.trauma_room(patient))
            trauma_end_time = env.now
            log_event(f"Patient {patient} left Trauma room at time {trauma_end_time}")
            write_event_to_csv(['Trauma_Room_Service_End_time', patient, trauma_end_time])
    else:
        with er_instance.nurses.request() as request:
            yield request
            triage_start_time = env.now
            log_event(f"Patient {patient} received by Triage at time {triage_start_time}")
            write_event_to_csv(['Triage_Start_time', patient, triage_start_time])
            yield env.process(er_instance.triage(patient))
            triage_end_time = env.now
            log_event(f"Patient {patient} completed Triage at time {triage_end_time}")
            write_event_to_csv(['Triage_End_time', patient, triage_end_time])

        with er_instance.exam_rooms.request() as request:
            yield request
            exam_room_start_time = env.now
            log_event(f"Patient {patient} arrived in exam room at time {exam_room_start_time}")
            write_event_to_csv(['Exam_Room_Service_Start_time', patient, exam_room_start_time])
            yield env.process(er_instance.exam_room(patient))
            exam_room_end_time = env.now
            log_event(f"Patient {patient} left exam room at time {exam_room_end_time}")
            write_event_to_csv(['Exam_Room_Service_End_time', patient, exam_room_end_time])

    needs_imaging = random.choice([True, False])
    if needs_imaging:
        with er_instance.imaging_rooms.request() as request:
            yield request
            yield env.process(er_instance.imaging(patient))
            log_event(f"Patient {patient} completed imaging at time {env.now}")
            
      # Doctor consultation for every patient
    with er_instance.consultation.request() as request:
        yield request
        yield env.process(er_instance.doctor_consultation(patient))
        log_event(f"Patient {patient} had a consultation at time {env.now}")

        # Decide whether to admit or discharge
    needs_admission = random.choice([True, False]) 
    if needs_admission:
        log_event(f"Patient {patient} admitted to the hospital at time {env.now}")
    else:
        log_event(f"Patient {patient} discharged from the ER at time {env.now}")


    wait_times.append(env.now - arrival_time)
    departure_time = env.now
    log_event(f"Patient {patient} left the ER at time {departure_time}")
    write_event_to_csv(['Patient_Departure', patient, departure_time])

# %%
def run_er(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms, num_imaging_rooms):
    er_instance = ER(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms, num_imaging_rooms)
    log_event("ER simulation run starts")
    for patient in range(3):
        env.process(go_to_er(env, patient, er_instance))

    while True:
        yield env.timeout(np.random.exponential(10))  # Wait a bit before generating a new patient 

        patient += 1
        env.process(go_to_er(env, patient, er_instance))

# %%
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    return average_wait


# %%
def get_user_input():
    num_reception = int(input("Input # of receptionists working: "))
    num_nurses = int(input("Input # of nurses working: "))
    num_doctors = int(input("Input # of doctors working: "))
    num_trauma_rooms = int(input("Input # of trauma rooms: "))
    num_exam_rooms = int(input("Input # of exam rooms: "))
    num_imaging_rooms = int(input("Input # of imaging rooms: "))
    return num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms,num_imaging_rooms


# %%
def main():
    # Reset the CSV file at the start
    write_event_to_csv([], mode='w')
    random.seed(42)
    num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms,num_imaging_rooms = get_user_input()

    total_simulation_runs = 10
    average_waiting_times = []
    log_event("Simulation starts")
    for _ in range(total_simulation_runs):
        wait_times.clear()  # Reset wait times for each simulation run
        env = simpy.Environment()
        env.process(run_er(env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms,num_imaging_rooms))
        env.run(until=120)

        avg_wait_time = get_average_wait_time(wait_times)
        average_waiting_times.append(avg_wait_time)
    log_event("Simulation ends")
    total_average_waiting_time = sum(average_waiting_times) / total_simulation_runs

    if total_average_waiting_time < 60:
        print("Goal achieved! The total average time in the ER is less than one hour.")
    else:
        print("Goal not achieved. The total average time in the ER is one hour or more.")

    print("The total average waiting time across {} runs is {:.2f} minutes.".format(total_simulation_runs, total_average_waiting_time))

if __name__ == "__main__":
    main()


