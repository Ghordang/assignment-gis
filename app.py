# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 15:31:20 2018

@author: Dano
"""

import json
from flask import Flask, render_template, jsonify
import psycopg2


app = Flask(__name__)


@app.route('/')
def idx():
    return render_template('index.html')

#testing coords
#lng=17.106173314294153
#lat=48.09946022758763
#rad=1000

@app.route('/destroyed/<params>/<rad>')
def blastRadius(params,rad):
    print("Params:",type(params),params)
    print("Rad", float(rad))
    lnglat=[float(x) for x in params.strip("LngLat(").strip(")").split(", ")]
    lng=lnglat[0]
    lat=lnglat[1]
    
    res=[]
    conn = psycopg2.connect("dbname='ba_wien' user='postgres' host='localhost' password='postgres' ")
    cursor = conn.cursor()
    cursor.execute("""
                   with center as (
                    	SELECT ST_SetSRID(ST_Point(%s, %s),4326) pnt
                    	)
                   SELECT st_asgeojson(ST_Transform(geometry(ST_Buffer(geography(pnt),%s)),4326)) rad FROM center
                   """, (lng,lat,rad))
    
    circ=cursor.fetchall()
    cursor.execute("""
                   
                    with center as (
                    	SELECT ST_SetSRID(ST_Point(%s, %s),4326) pnt
                    	),
                    radius as(
                    	SELECT ST_Transform(geometry(ST_Buffer(geography(pnt),%s)),4326) rad FROM center	)						
                    select name, st_asgeojson(st_transform(way,4326)) from buildings
                    cross join radius
                    where 1=1
                    	and ST_Intersects(st_transform(way,4326) , radius.rad) = true
			
                   """, (lng,lat,rad))
    buildings = cursor.fetchall()
    print("Getting data")
    res=[{"type":"Feature", "geometry":json.loads(p[1])} for p in buildings]
    crc=[{"type":"Feature", "geometry":json.loads(p[0])} for p in circ]
    
    return jsonify({"data": res,"crc":crc, "count":len(res)}) 


name =None


def hospName(name):
    if name ==None:
        name="Unknown hospital"
    return name
@app.route('/hospitals/<params>/<rad>')
def nearestHospitals(params,rad):
    print("Params:",type(params),params)
    print("Rad", float(rad))
    lnglat=[float(x) for x in params.strip("LngLat(").strip(")").split(", ")]
    lng=lnglat[0]
    lat=lnglat[1]
    
    res=[]
    conn = psycopg2.connect("dbname='ba_wien' user='postgres' host='localhost' password='postgres' ")
    cursor = conn.cursor()
    cursor.execute("""
                                   
                                 		
                with center as (
                	SELECT ST_SetSRID(ST_Point(%s, %s),4326) pnt
                	), radius as(
                	SELECT ST_Transform(geometry(ST_Buffer(geography(pnt),%s)),4326) rad FROM center	)	
                select name, st_distance(t_way::Geography,radius.rad::Geography) dist, st_asgeojson(ST_Centroid(t_way)) pnt from buildings
                cross join radius
                where 1=1
                	and building = 'hospital'
                	and ST_Contains(radius.rad,t_way) != true
                order by dist
                limit 5

			
                   """, (lng,lat,rad))
    hosps = cursor.fetchall()
    print("Getting data")
    res=[{"type":"Feature", "geometry":json.loads(p[2]), "properties": {"name": hospName(p[0]), "distance": round(p[1]/1000,2)}} for p in hosps]
    
    return jsonify({"data": res}) 


@app.route('/pipebuild/<params>/<rad>')
def affectedPipelines(params,rad):
    print("Params:",type(params),params)
    print("Rad", float(rad))
    lnglat=[float(x) for x in params.strip("LngLat(").strip(")").split(", ")]
    lng=lnglat[0]
    lat=lnglat[1]
    
    res=[]
    conn = psycopg2.connect("dbname='ba_wien' user='postgres' host='localhost' password='postgres' ")
    cursor = conn.cursor()
    #select all affected pipelines
    cursor.execute("""
                                   
with center as (
		SELECT ST_SetSRID(ST_Point(%s, %s),4326) pnt
	), radius as(
		SELECT ST_Transform(geometry(ST_Buffer(geography(pnt),%s)),4326) rad FROM center	),
	affected as (
		select t_way, st_length(t_way::geography) leng from pipelines
		cross join radius
		where st_intersects(t_way, radius.rad)
	)
select st_asgeojson(t_way), leng from affected
			
                   """, (lng,lat,rad))
    pipelines = cursor.fetchall()
    #select all buildings affected by pipelines
    cursor.execute("""
    
        with center as (
        		SELECT ST_SetSRID(ST_Point(17.13352352272554, 48.15620123577739),4326) pnt
        	), radius as(
        		SELECT ST_Transform(geometry(ST_Buffer(geography(pnt),2500)),4326) rad FROM center	),
        	affected as (
        		select t_way, st_length(t_way::geography) leng from pipelines
        		cross join radius
        		where st_intersects(t_way, radius.rad)
        	)
        select st_asgeojson(buildings.t_way) from affected
        cross join buildings
        where 1=1
        and st_intersects(affected.t_way, buildings.t_way)

    """, (lng,lat,rad))
    pb=cursor.fetchall()
    
    print("Getting data")
    pb_res=[{"type":"Feature", "geometry":json.loads(p[0])} for p in pb]

    res=[{"type":"Feature", "geometry":json.loads(p[0]), "properties": {"leng": round(p[1]/1000,3)}} for p in pipelines]
    
    return jsonify({"data": res, "pb":pb_res}) 



if __name__ == '__main__':
    app.run(debug=True)
