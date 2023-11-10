drop table  public.electric_vehicle_pop_data;
create table public.electric_vehicle_pop_data
(
VIN varchar(30),
County	varchar(20),
City  varchar(50),
State  char(2),	
Postal_Code int,
Model_Year int,
Make  varchar(20),
Model  varchar(50),
Electric_Vehicle_Type  varchar(50),
CAFV_Eligibility  varchar(100),
Electric_Range  int,
Base_MSRP int, 
Legislative_District int,
DOL_Vehicle_ID varchar(20),
Vehicle_Location varchar(50),
Electric_Utility varchar(200),
Census_Tract varchar(50)
)
;