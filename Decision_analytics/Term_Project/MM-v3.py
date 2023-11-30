import simpy
import numpy as np
import random
import statistics

# Global variables
wait_times = []
global_clock = 0

# Function to log events
def log_event(message):
    global global_clock
    print(f"Time {global_clock}: {message}")

# Function to write events to a CSV file
def write_event_to_csv(event_data, mode='a'):
    # Your CSV writing logic goes here
    pass

class ER(object):
    def __init__(self, env, num_receptionists, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms, num_imaging_rooms):
        self.env = env
        self.receptionists = simpy.Resource(env, num_receptionists)
        self.nurses = simpy.Resource(env, num_nurses)
        self.doctors = simpy.Resource(env, num_doctors)
        self.trauma_rooms = simpy.Resource(env, num_trauma_rooms)
        self.exam_rooms = simpy.Resource(env, num_exam_rooms)
        self.imaging_rooms = simpy.Resource(env, num_imaging_rooms)
        self.consultation = simpy.Resource(env, num_doctors) # Assuming doctors do the consultation

        # Utilization tracking
        self.receptionists_utilization = 0
        self.nurses_utilization = 0
        self.doctors_utilization = 0
        self.trauma_rooms_utilization = 0
        self.exam_rooms_utilization = 0
        self.imaging_rooms_utilization = 0
        
        # Duration tracking
        self.arrival_durations = []
        self.triage_durations = []
        self.exam_room_durations = []
        self.trauma_room_durations = []
        self.imaging_durations = []
        self.consultation_durations = []
        
    def arrival(self, patient):
        arrival_interval = np.random.poisson(5)
        yield self.env.timeout(arrival_interval)
        event_data = ['Arrival', patient, self.env.now]

    def triage(self, patient):
        arrival_time = self.env.now
        service_time = np.random.exponential(10)
        with self.nurses.request() as request:
            yield request
            service_start_time = self.env.now
            self.nurses_utilization += service_time
            yield self.env.timeout(service_time)
            service_end_time = self.env.now
            log_event(f"Patient {patient} completed Triage at time
            {service_end_time}")
            write_event_to_csv(['Triage_End_time', patient, service_end_time])
            self.nurses_utilization -= service_time
            
            # Record the total time (service time + queue wait time)
            total_time = service_end_time - arrival_time
            self.triage_durations.append(total_time)

    def exam_room(self, patient):
        arrival_time = self.env.now
        service_time = max(1, np.random.normal(15, 5))
        with self.exam_rooms.request() as request:
            yield request
            service_start_time = self.env.now
            self.exam_rooms_utilization += service_time
            yield self.env.timeout(service_time)
            service_end_time = self.env.now
            log_event(f"Patient {patient} left exam room at time {service_end_time}")
            write_event_to_csv(['Exam_Room_Service_End_time', patient, service_end_time])
            self.exam_rooms_utilization -= service_time

        # Record the total time (service time + queue wait time)
        total_time = service_end_time - arrival_time
        self.exam_room_durations.append(total_time)
        
def trauma_room(self, patient):
    arrival_time = self.env.now
    service_time = max(1, np.random.normal(20, 7))
    with self.trauma_rooms.request() as request:
        yield request
        service_start_time = self.env.now
        self.trauma_rooms_utilization += service_time
        yield self.env.timeout(service_time)
        service_end_time = self.env.now
        log_event(f"Patient {patient} left Trauma room at time {service_end_time}")
write_event_to_csv(['Trauma_Room_Service_End_time', patient,
service_end_time])
self.trauma_rooms_utilization -= service_time
# Record the total time (service time + queue wait time)
total_time = service_end_time - arrival_time
self.trauma_room_durations.append(total_time)

def imaging(self, patient):
arrival_time = self.env.now
service_time = np.random.exponential(15)
with self.imaging_rooms.request() as request:
yield request
service_start_time = self.env.now
self.imaging_rooms_utilization += service_time
yield self.env.timeout(service_time)
service_end_time = self.env.now
log_event(f"Patient {patient} completed imaging at time
{service_end_time}")
self.imaging_rooms_utilization -= service_time
# Record the total time (service time + queue wait time)
total_time = service_end_time - arrival_time
self.imaging_durations.append(total_time)

def doctor_consultation(self, patient):
arrival_time = self.env.now
service_time = np.random.exponential(12)
with self.consultation.request() as request:
yield request
service_start_time = self.env.now
self.doctors_utilization += service_time
yield self.env.timeout(service_time)
service_end_time = self.env.now
log_event(f"Patient {patient} had a consultation at time
{service_end_time}")
write_event_to_csv(['Doctor_Consultation_End_time', patient,
service_end_time])
self.doctors_utilization -= service_time
# Record the total time (service time + queue wait time)
total_time = service_end_time - arrival_time
self.consultation_durations.append(total_time)

def print_average_durations(self):
# Print average durations for each step
print("Average Arrival Duration:", np.mean(self.arrival_durations))
print("Average Triage Duration:", np.mean(self.triage_durations))
print("Average Exam Room Duration:", np.mean(self.exam_room_durations))
print("Average Trauma Room Duration:", np.mean(self.trauma_room_durations))
print("Average Imaging Duration:", np.mean(self.imaging_durations))
print("Average Consultation Duration:",
np.mean(self.consultation_durations))

def print_resource_utilization(self):
print("Receptionists utilization:", self.receptionists_utilization)
print("Nurses utilization:", self.nurses_utilization)
print("Doctors utilization:", self.doctors_utilization)
print("Trauma Rooms utilization:", self.trauma_rooms_utilization)
print("Exam Rooms utilization:", self.exam_rooms_utilization)
print("Imaging Rooms utilization:", self.imaging_rooms_utilization)

# Updated service time functions
def triage(env, patient, er_instance):
service_time = np.random.exponential(10)
with er_instance.nurses.request() as request:
yield request
service_start_time = env.now
er_instance.nurses_utilization += service_time
yield env.timeout(service_time)
service_end_time = env.now
log_event(f"Patient {patient} completed Triage at time {service_end_time}")
write_event_to_csv(['Triage_End_time', patient, service_end_time])
er_instance.nurses_utilization -= service_time

# Updated service time functions
def exam_room(env, patient, er_instance):
service_time = np.random.exponential(15)
with er_instance.exam_rooms.request() as request:
yield request
service_start_time = env.now
er_instance.exam_rooms_utilization += service_time
yield env.timeout(service_time)
service_end_time = env.now
log_event(f"Patient {patient} left exam room at time {service_end_time}")
write_event_to_csv(['Exam_Room_Service_End_time', patient,
service_end_time])
er_instance.exam_rooms_utilization -= service_time

def trauma_room(env, patient, er_instance):
service_time = np.random.exponential(20)
with er_instance.trauma_rooms.request() as request:
yield request
service_start_time = env.now
er_instance.trauma_rooms_utilization += service_time
yield env.timeout(service_time)
service_end_time = env.now
log_event(f"Patient {patient} left Trauma room at time {service_end_time}")
write_event_to_csv(['Trauma_Room_Service_End_time', patient,
service_end_time])
er_instance.trauma_rooms_utilization -= service_time

def imaging(env, patient, er_instance):
service_time = np.random.exponential(15)
with er_instance.imaging_rooms.request() as request:
yield request
service_start_time = env.now
er_instance.imaging_rooms_utilization += service_time
yield env.timeout(service_time)
service_end_time = env.now
log_event(f"Patient {patient} completed imaging at time
{service_end_time}")
er_instance.imaging_rooms_utilization -= service_time

def doctor_consultation(env, patient, er_instance):
service_time = np.random.exponential(12)
with er_instance.consultation.request() as request:
yield request
service_start_time = env.now
er_instance.doctors_utilization += service_time
yield env.timeout(service_time)
service_end_time = env.now
log_event(f"Patient {patient} had a consultation at time
{service_end_time}")
write_event_to_csv(['Doctor_Consultation_End_time', patient,
service_end_time])
er_instance.doctors_utilization -= service_time

def go_to_er(env, patient, er_instance):
arrival_time = env.now
log_event(f"Patient {patient} arrived in ER at time {arrival_time}")
write_event_to_csv(['Patient_Arrival', patient, arrival_time])
# New logic to determine if a patient needs immediate care
needs_immediate_care = random.choice([True, False]) # Example condition
if needs_immediate_care:
yield env.process(er_instance.trauma_room(patient)) # Pass er_instance
else:
yield env.process(er_instance.triage(patient)) # Pass er_instance
yield env.process(er_instance.exam_room(patient)) # Pass er_instance
needs_imaging = random.choice([True, False])
if needs_imaging:
yield env.process(er_instance.imaging(patient)) # Pass er_instance
yield env.process(er_instance.doctor_consultation(patient)) # Pass er_instance
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

def run_er(env, er_instance, arrival_rate):
global global_clock
log_event("ER simulation run starts")
patient = 0
while True:
inter_arrival_time = np.random.poisson(1 / arrival_rate)
yield env.timeout(inter_arrival_time)
global_clock = env.now
env.process(go_to_er(env, patient, er_instance))
patient += 1

def get_average_wait_time(wait_times):
average_wait = statistics.mean(wait_times)
minutes, frac_minutes = divmod(average_wait, 1)
seconds = frac_minutes * 60
return round(minutes), round(seconds)
num_receptionists = 3
num_nurses = 15
num_doctors = 20
num_trauma_rooms = 10
num_exam_rooms = 10
num_imaging_rooms = 5
arrival_rate = 1

def main():
# Reset the CSV file at the start
write_event_to_csv([], mode='w')
#num_receptionists, num_nurses, num_doctors, num_trauma_rooms, num_exam_rooms,
num_imaging_rooms, arrival_rate = get_user_input()
total_simulation_runs = 2
average_waiting_times = []
log_event("Simulation starts")
for _ in range(total_simulation_runs):
wait_times.clear() # Reset wait times for each simulation run
env = simpy.Environment()
er_instance = ER(env, num_receptionists, num_nurses, num_doctors,
num_trauma_rooms, num_exam_rooms, num_imaging_rooms)
env.process(run_er(env, er_instance, arrival_rate))
env.run(until=180) # Increased simulation duration to 180 time units
mins, secs = get_average_wait_time(wait_times)
average_waiting_times.append(mins + secs / 60)
# Log average waiting time for each run
log_event(f"Average waiting time for run {_ + 1}: {mins} minutes and {secs}
seconds")
# Print resource utilization for each run
er_instance.print_resource_utilization()
er_instance.print_average_durations()
log_event("Simulation ends")
total_average_waiting_time = sum(average_waiting_times) / total_simulation_runs
if total_average_waiting_time < 60:
print("Goal achieved! The total average time in the ER is less than one
hour.")
else:
print("Goal not achieved. The total average time in the ER is one hour or
more.")
print("The total average waiting time across {} runs is {:.2f}
minutes.".format(total_simulation_runs, total_average_waiting_time))
if __name__ == "__main__":
main()
