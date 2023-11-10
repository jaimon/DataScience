
drop table public.meteorite_landings;
create table public.meteorite_landings
(
name varchar(50),	
id varchar(20),
nametype varchar(10),
recclass varchar(50),
mass numeric,
fall char(10),
year char(4),
reclat numeric(10,3),
reclong	numeric(10,3),
GeoLocation varchar(50)
)