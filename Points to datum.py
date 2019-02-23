# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:44:57 2016

@author: REDACTED
"""

#THIS PROGRAM FINDS THE POINT ON THE REFERENCE LINE
#WHICH IS CLOSEST TO EACH DATA POINT

import json
import shapely.geometry as geom


#Open the two files and import the data
exported_file = open('export_file_5.json','r')
commute_journeys = json.load(exported_file)
exported_file.close()

exported_file = open('datum_lines_xy','r')
datum_points = json.load(exported_file)
exported_file.close()

datum_for_plot = []

#Make these into a list
#Loop through all points in the datum
for point_no in range(len(datum_points)):
	datum_point = datum_points[point_no]
	x = datum_point['x']
	y = datum_point['y']
	
	#Append everything into a list of the form that shapely wants.
	datum_for_plot.append((x,y))

#Now call that a line.
line = geom.LineString(datum_for_plot)

#Looping through all the commutes
for commute_no in range(len(commute_journeys)):
	commute = commute_journeys[commute_no]
	trackPoints = commute['trackPoints']
		
		#Now set up all the points as shapely objects
		#THIS IS THE CODE FROM KINGTON (2013)
		#(with changes)
		    for point_no in range(len(trackPoints)-1):
        	trackPoint = trackPoints[point_no]
        	point = geom.Point(trackPoint['x'], trackPoint['y'])
        	
        	#Determine the distance from each point to the datum line
        	distance = line.distance(point)
        	
        	trackPoint['datum']=distance
        	
        	#If it's less than 100m, then put into the trackPoint data
        	#some info about the datum location
        	if distance<100:
				point_on_line = line.interpolate(line.project(point))
				trackPoint['datum']= {'x':point_on_line.x,\
				'y':point_on_line.y, 'datum':line.project(point)}
						
#Write to a file.
exported_file = open('export_file_6.json','w')
json.dump(commute_journeys, exported_file)
exported_file.close()
