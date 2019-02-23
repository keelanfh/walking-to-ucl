# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:44:57 2016

@author: REDACTED
"""

#This program splits the datum line into segments,
#and then averages the speeds of all journeys matching these segments

#Import the relevant libraries
import json
import shapely.geometry as geom
import numpy as np
import pyproj as pp

#Open the data about the journeys
exported_file = open('export_file_6.json','r')
commute_journeys = json.load(exported_file)
exported_file.close()

#Set the length of the datum (5km) and create empty lists for the speeds
datum_length = 5000
datum_speeds = [0] * datum_length
datum_averages = [0] * datum_length

for datum_point in range(int(datum_length/10)):

	#Split the datum into 10m long sections
	min = 10 * (float(datum_point))
	max = 10 * (float(datum_point + 1))
	
	#Create an empty list for each of the sections
	datum_speeds[datum_point]=[]
	
	#Looping through all the commutes and all the trackPoints
	for commute_no in range(len(commute_journeys)):
		commute = commute_journeys[commute_no]
		
		#Only include those which started at home
		if commute['from_location'] == 'home':
			trackPoints = commute['trackPoints']
			for point_no in range(len(trackPoints)):
				trackPoint = trackPoints[point_no]
				
				#Only proceed if we've already assigned datum
				#information to the trackPoint
				if 'datum' in trackPoint and \
				type(trackPoint['datum'])==dict:
					datum = trackPoint['datum']['datum']
					
					#If in the range, append the speed
					#to the list of speeds
					if datum > min and datum < max:
						datum_speeds[datum_point].append(trackPoint['speed'])
						
	#Take an average of the speeds and assign it to the list of averages
	datum_averages[datum_point] = np.average(datum_speeds[datum_point])
	
#Set up a suitable GeoJSON formatted dictionary for the results
results = {
	u'type': u'FeatureCollection',
	u'features': []
	}
	
#Alias the relevant bit
export_features = results['features']

#Open the datum file
exported_file = open('datum_lines_xy','r')
datum_points = json.load(exported_file)
exported_file.close()

#Make these into a list
#Loop through all points in the datum
datum_for_plot=[]

for point_no in range(len(datum_points)):
	datum_point = datum_points[point_no]
	datum_averages[point_no]={'speed':datum_averages[point_no]}
	x = datum_point['x']
	y = datum_point['y']
	datum_averages[point_no]['x']=datum_point['x']
	datum_averages[point_no]['y']=datum_point['y']
	
	#Append everything into a list of the form that shapely wants.
	datum_for_plot.append((x,y))

#Now call that a line in shapely.
line_string = geom.LineString(datum_for_plot)

#Set up the two projections
p1 = pp.Proj(proj='latlong',datum='WGS84')
p2 = pp.Proj(proj="utm",zone=30,datum='WGS84')

#Convert the x and y to lat and lon
for item_no in range(len(datum_averages)):
    item = datum_averages[item_no]
    if type(item) == dict:
    	item['lat'],item['lon']=pp.transform(p2,p1,item['x'],item['y'])

#Add everything to the GeoJSON dictionary

for point in range(len(datum_averages)-1):
		
    	line_data = datum_averages[point]
    	line_data2 = datum_averages[point+1]
    	if type(line_data2) == dict and type(line_data) == dict:
		
			#create a suitable GeoJSON object with the speed as a property
			line = {
						u'geometry': 
							{
								u'type':u'LineString',
								u'coordinates': [[line_data['lon'],		\
			 line_data['lat']],[line_data2['lon'],line_data2['lat']]]
							}, 
						u'type': u'Feature',
						u'properties':
							{
							u'speed': line_data['speed']
							}
					}
		
			#Append this object to the list
			export_features.append(line)

#Write to a file.
exported_file = open('datum_speeds_home.json','w')
json.dump(results, exported_file)
exported_file.close()
