# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:05:55 2016

@author: REDACTED
"""

#THIS PROGRAM PLOTS GRAPHS BASED ON MOVING AVERAGES
#AND LINEAR REGRESSION

#Import the relevant libraries
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

#Open the file
exported_file = open('export_file_5.json','r')
commute_journeys = json.load(exported_file)
exported_file.close()

#Set up lists we can put the sorted commutes into
speeds_down = []
speeds_up = []
speeds_neutral = []

#Function for putting the data into a form that we can plot
#Add this data to a list.
x=0
y=0
reference_times = []
neutral_commutes = []
speeds = []
def process_data(speeds_list):

	print commute['i_d']
	reference_times = []
	speeds = []
	
	for point in range(len(trackPoints)-3):
		if 'speed_pavg' in trackPoints[point+2]:
		#Put all the speed data into a list, paired with times
		#for speed/time plot
			reference_times.append(trackPoints[point+2]['reference_time'])
			speeds.append(trackPoints[point+2]['speed_pavg'])
			
	# 100 linearly spaced numbers
	x = np.linspace(0,commute['duration'],100)
	
	#A straight line based on the linear regression numbers
	y = commute['linr_pavg']['intercept'] + \
	commute['linr_pavg']['slope']*x

	plot()
	speeds_list.append(speed)

#A function for running the plot
def plot():
	#Set up a new figure for each commute
	plt.figure(commute['i_d'])
	#Label it so we can see it
	plt.title(commute['i_d'])
	#Label the axes
	plt.xlabel("time (s)")
	plt.ylabel("speed (m/s)")
	#Plot the line
	plt.plot(x,y)
	#Plot the data
	plt.plot(reference_times,speeds)
	#Set the axis values
	plt.axis([0,1600,0,6])

#Selecting the data that we've identified as increasing/decreasing
#speed journeys
for commute_no in range(len(commute_journeys)):
	commute = commute_journeys[commute_no]
	trackPoints = commute['trackPoints']
	
	#Only process those journeys that have had a period average
	#(some were too short for this to take place)
	if 'linr_pavg' in commute:
	
		speed = commute['distance']/float(commute['duration'])
		
		#speeds_down will be those which  have r<-0.4
		if commute['linr_pavg']['r']<-0.4: 
		
			process_data(speeds_down)
		
		#speeds_up will be those which have r>0.4						
		elif commute['linr_pavg']['r']>0.4:
		
			process_data(speeds_up)
		
		#everything else goes into the speeds_neutral list			
		else:
		
			process_data(speeds_neutral)
			neutral_commutes.append(commute_no)

#Printing averages and t-test results for whatever we want
def compare(one,two):

	print np.average(one)
	print np.average(two)
	print stats.ttest_ind(one, two, axis=0, equal_var=True)
	
compare(speeds_down, speeds_up)