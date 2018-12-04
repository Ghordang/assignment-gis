CREATE EXTENSION postgis;


select * from spatial_ref_sys

select * from planet_osm_line limit 200

CREATE EXTENSION postgis_sfcgal;
CREATE EXTENSION address_standardizer;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_tiger_geocoder;


create extension postgis;


WITH parky AS (
      SELECT * FROM planet_osm_polygon p
      WHERE leisure = 'park'
    )
    SELECT osm_id, name, way as geojson FROM parky





