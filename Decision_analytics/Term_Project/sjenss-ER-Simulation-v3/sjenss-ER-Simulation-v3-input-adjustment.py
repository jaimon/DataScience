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

    # Service times for arrival
    def arrival(self, patient):
        # Exponential distribution of 12 patients per hour (12 patients will arrive at the ER per hour)
        arrival_rate = 12 / 60
        service_time = np.random.exponential(1 / arrival_rate)
        yield self.env.timeout(service_time)
        self.env.process(self.reception_process(patient))
        event_data = ['Arrival', patient, self.env.now]
    
    # Process for going through reception (check-in)
    def reception_process(self, patient):
        with self.reception.request() as request:
            yield request
            reception_service_time = np.random.exponential(5) # 5 minutes per patient on average for check-in
            yield self.env.timeout(reception_service_time)
            event_data = ['Reception', patient, self.env.now]


    # Service times for triage
    def triage(self, patient):
        with self.nurses.request() as request:
            yield request
            # Triage takes about 10 minutes on average (6 per hour)
            service_time = np.random.exponential(10)
            yield self.env.timeout(service_time)
            event_data = ['Triage', patient, self.env.now]

    # Service times for exam rooms
    def exam_room(self, patient):
        with self.exam_rooms.request() as request:
            yield request
            # An exam room will occupied for approximately 30 minutes on average (2 occupants per hour)
            service_time = np.random.exponential(30)
            yield self.env.timeout(service_time)
            event_data = ['Exam_room', patient, self.env.now]

    # Service times for trauma rooms
    def trauma_room(self, patient):
        with self.trauma_rooms.request() as request:
            yield request
            # A trauma room will be occupied for approximately 45 minutes on average (1.33 occupants per hour)
            service_time = np.random.exponential(45)
            yield self.env.timeout(service_time)
            event_data = ['Trauma_room', patient, self.env.now]


    # Service times for imaging
    def imaging(self, patient):
        with self.imaging_rooms.request() as request:
            yield request
            # Imaging takes approximately 15 minutes on average (4 per hour)
            service_time = np.random.exponential(15)
            yield self.env.timeout(service_time)
            event_data = ['Imaging', patient, self.env.now]

    # Service times for doctor consultation
    def doctor_consultation(self, patient):
        with self.doctors.request() as request:
            yield request
        # A doctor consultation takes 12 minutes on average (5 per hour)
        service_time = np.random.exponential(12)
        yield self.env.timeout(service_time)
        event_data = ['Consultation', patient, self.env.now]

# %%
def go_to_er(env, patient, er_instance):
    arrival_time = env.now
    log_event(f"Patient {patient} arrived in ER at time {arrival_time}")
    write_event_to_csv(['Patient_Arrival', patient, arrival_time])

    """
    New logic to determine if a patient needs immediate care
    On average, approximately 1 in 10 patients will need immediate care.
    Therefore, we will use a random number generator to determine if a patient needs immediate care.
    If the random number is less than 0.1, the patient will need immediate care.
    Otherwise, the patient will go through the normal process.
    """
    needs_immediate_care = random.random() < 0.1

    if needs_immediate_care:
         with er_instance.trauma_rooms.request() as request: # Changed resource request to trauma room
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
    
    """
    New logic to determine if a patient needs imaging
    On average, approximately 65% of patient will need imaging/testing of some sort.
    Therefore, we will use a random number generator to determine if a patient needs imaging.
    If the random number is less than 0.65, the patient will need testing.
    Otherwise, the patient will go straight to the doctor consulation.
    """
    needs_imaging = random.random() < 0.65
    
    if needs_imaging:
        with er_instance.imaging_rooms.request() as request:
            yield request
            yield env.process(er_instance.imaging(patient))
            log_event(f"Patient {patient} completed imaging at time {env.now}")
            
    # Doctor consultation for every patient
    with er_instance.doctors.request() as request: # resource request changed to doctor from consultation
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
    if not wait_times:
        return 0, 0
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

#%%

