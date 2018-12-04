# First response app



The app is aimed to provide information for first responders after a bombing or other detonation event.Contains data fro Bratislava and Wien aglomeration.
The app can be used to identify number of potentially affected buildings, power and gaslines that were affected and buildings potentially affected by secondary damage through powerlines.

### Usage and scenarios:
  - User can select blast radius and click on map to mark a detonation point/multiple detonation points
  - Displaying buildings affected by the detonation
  - Displaying closest nearby unaffected hospitals with names and distances to them
  - Finding affected powerlines and potentially affected building outside of detonation radius

![screenshot.jpg](https://github.com/Ghordang/assignment-gis/blob/master/screenshot.jpg "App screenshot")

### App and technologies:
The application consists of three different parts:
- Postgresql 10 database with PostGIS to store and calculate geodata
- Flask server to serve the data in form of geojson and to serve html template
- [Mapbox] to display geojsons and get user interaction

All the frontend code is contained in index.html.
Data were collected from the openstreetmap database and contain area from Bratislava to Wien: ~1.8GB

### Database structure
Tables:
- Buildings: storing all information about buildings and their respective coordinates
- Pipelines: storing all information about pipelines and their respective coordinates

Tables were created from openstreetmap data tables while converting the "way" column from merkator projection to EPSG4326.

~~~~
create table pipelines as
select *,st_transform(way,4326) t_way 
from planet_osm_line
where 1=1
	and route='pipeline'
	or power='line'
	or man_made = 'pipeline'
~~~~

After that the column was indexed.
~~~~
CREATE INDEX p_index ON pipelines USING GIST ( t_way ); 
~~~~
(Buildings table and index was analogous for buildings)

With not having to do the projection transformation during run, *the time necessary for querying dropped to 1/100*.
After using the GIST index on transformed "way" column, the time necessary for querying went down by another *1/4*.



### Explained sample query:
~~~~
--selecting all buildings that have powerlines that run underneath/above them
--center is center point for detonation with sample coordinates
--radius is detonation circle with sample radius
with center as (
		SELECT ST_SetSRID(ST_Point(17.13352352272554, 48.15620123577739),4326) pnt
	), radius as(
		SELECT ST_Transform(geometry(ST_Buffer(geography(pnt),2500)),4326) rad FROM center	),
	affected as (
		select t_way, st_length(t_way::geography) leng from pipelines
		cross join radius
		where st_intersects(t_way, radius.rad)
	)
select buildings.t_way from affected
cross join buildings
where 1=1
and st_intersects(affected.t_way, buildings.t_way)
~~~~




