# %%
import simpy
import random
import statistics
import os

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
    def __init__(self, env, num_reception, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms):
        self.env = env
        self.reception = simpy.Resource(env, num_reception)
        self.nurses = simpy.Resource(env, num_nurses)
        self.doctors = simpy.Resource(env, num_doctors)
        self.trauma_rooms = simpy.Resource(env, num_trauma_rooms)
        self.exam_rooms = simpy.Resource(env, num_exam_rooms)

#service times
    def arrival(self, patient):
        yield self.env.timeout(random.randint(1, 30))
        event_data = ['Arrival', patient, self.env.now]
        #log_event(f"Patient {patient}  arrived at time {self.env.now}")
        #write_event_to_csv(event_data)
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

    with er_instance.nurses.request() as request:
        yield request
        triage_start_time = env.now
        log_event(f"Patient {patient} received by Triage at time {triage_start_time}")
        write_event_to_csv(['Triage_Start_time', patient, triage_start_time])
        yield env.process(er_instance.triage(patient))
        triage_end_time = env.now
        log_event(f"Patient {patient} completed Triage at time {triage_end_time}")
        write_event_to_csv(['Triage_End_time', patient, triage_end_time])


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


