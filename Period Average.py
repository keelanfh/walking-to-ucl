# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 10:57:53 2016

@author: REDACTED
"""
#THIS PROGRAM TAKES MOVING AVERAGES
#AND THEN RUNS REGRESSION ANALYSIS

#Import relevant libraries
import json
from scipy import stats
import numpy as np

#Open the file and load it as an object
exported_file = open('export_file_4.json','r')
commute_journeys = json.load(exported_file)
exported_file.close()

#Looping through all the commutes
for commute_number in range(len(commute_journeys)):

	reference_times = []
	speeds = []
	
	commute = commute_journeys[commute_number]
	trackPoints = commute['trackPoints']
	
	if len(trackPoints)>=0:
		
		#We have a reduced number of points
		#(we can't period average at the edges)
		for point_number in range(len(trackPoints)-4):
			#This will be the central point
			point_number_2 = point_number + 2
			point = trackPoints[point_number_2]
			#Points one to the left and right
			pointL = trackPoints[point_number_2-1]
			pointR = trackPoints[point_number_2+1]

			#Take the average
			speed_pavg = np.average([point['speed'],pointL['speed'],\
			pointR['speed']])
			#Put the average in to the data about the point
			point['speed_pavg'] = speed_pavg
			reference_times.append(point['reference_time'])
			speeds.append(speed_pavg)
   
        if reference_times != []:
        	ref_test = True
        	
        #Linear regression based on the moving average values
		commute['linr_pavg']={}
		linr = commute['linr_pavg']
		linr['slope'], linr['intercept'], linr['r'], linr['p'],\
		linr['std_err'] = stats.linregress(reference_times,speeds)

#Write to a file.
exported_file = open('export_file_5.json','w')
json.dump(commute_journeys, exported_file)
exported_file.close()