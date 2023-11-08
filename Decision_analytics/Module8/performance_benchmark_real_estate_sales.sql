drop table  public.real_estate_sales;
create table public.real_estate_sales
(
Serial_Number varchar(20),
List_Year varchar(4),
Date_Recorded date,
Town varchar(20),
Address	varchar(100),
Assessed_Value numeric,
Sale_Amount decimal(20,2),
Sales_Ratio decimal(10,2),
Property_Type varchar(50),
Residential_Type varchar(50),
NonUse_Code varchar(50),
Assessor_Remarks varchar(100),
OPM_remarks varchar(150),
location varchar(50)
)
;