# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 10:47:51 2016

@author: REDACTED
"""

#This program imports the relevant data from the Moves API
#It calculates the speeds at all points within each commute
#It then exports the data to a GeoJSON file for plotting

import datetime as dt
import json

from geopy.distance import vincenty
from moves import Moves

#Input the authorisation information for the Moves API
m = Moves("REDACTED","REDACTED","REDACTED")

# Set up a list of the locations we're interested in.
my_locs = [
    {
        'name': 'home',
        'lat' : 51.5376610267,
        'lon' : -0.1334586581
        },
    {
        'name': 'work',
        'lat' : 51.5245335649,
        'lon' : -0.134065590859
        }
    ]

# A function to check if the distance between two locations
# is less than a set distance        
def compare_dim(one,two,d):
    dist = vincenty(one, two).meters
    print dist
    if dist<d:
        return True
    else:
        return False
        
        
def compare_loc(sample, rules):
#Check if a location matches one of the locations in the list
    sample_lat = float(sample['lat'])
    sample_lon = float(sample['lon'])
    sample_loc = (sample_lat,sample_lon)
    for rule in rules:
    	rule_loc = (rule['lat'],rule['lon'])
        if compare_dim(rule_loc,sample_loc,500) == True:
                return rule['name']
    return False
    
def append_path(any_list):
#Add a path to the list of paths
	any_list.append({
        'from_location': from_location_name,
        'data': move_segment['activities'][0],
        })

#This is the access token that allows us to access the data from Moves
access_token = "REDACTED"

#Set up a list for the dates
dates_list = []
#Start date here
start_date = dt.date(2015,9,1)
#Step for data requests
step = dt.timedelta(6)
today = dt.date.today()

#Go through all the dates from the start date to today
for x in range(100):
    if (start_date + step)<today:
        date_set = [start_date, start_date + step]
        start_date += step
        dates_list.append(date_set)
    else:
        date_set = [start_date, today]
        dates_list.append(date_set)
        break
        
#Set up a list for us to dump all the journeys
commute_journeys=[]

#COLLECTING ALL THE DATA:

for date_set in dates_list:
    
    #Get the data from the Moves API.
    #Date converted into the way Moves wants it.
    from_date = date_set[0].strftime('%Y%m%d') 
    to_date = date_set[1].strftime('%Y%m%d')
    
    #Here we're calling the moves library.
    data = m.get_storyline(access_token,from_date,to_date, 'true')
    
    #Now that we have the data, let's pick out what we want
    for day in range(len(data)):
        segments = data[day]['segments']
        if segments != None:
                                    
            counter = 0
            
            for segment in segments:
            
            #We're only interested in journeys that start at a place
                if segment['type'] == 'place':
                    
                    #See if the location is one of the ones in the list
                    #then name it as that.
                    #compare_loc will return False if there is no match
                    from_location_name = \
                    compare_loc(segment['place']['location'],my_locs)
                    
                    #Only proceed if there is a valid location name
                    if from_location_name != False:
                        
                        #Only proceed if there are enough segments
                        if len(segments)>counter+2:
                        	#Name the subsequent segments.
                            move_segment = segments[counter+1]
                            to_segment = segments[counter+2]
                            
                            #Check if the segments are of the right type
                            #(We want a sequence of place-move-place)
                            if move_segment['type'] == 'move':
                                if to_segment['type'] == 'place':
                                    
                                    to_location = \
                                    to_segment['place']['location']
                                    to_location_name = \
                                    compare_loc(to_location, my_locs)
                                    
                                    #If they are valid pairs,
                                	#add to the list of commutes.
                                    if from_location_name == 'home':
                                        if to_location_name == 'work':
                                            append_path(commute_journeys)
                                    if from_location_name == 'work':
                                        if to_location_name == 'home':
                                            append_path(commute_journeys)
                counter += 1            
            
#Function to extract the date and time from a Moves output
def time_parser(time):
    time = str(time)
    y=int(time[0:4])
    m=int(time[4:6])
    d=int(time[6:8])
    h=int(time[9:11])
    mi=int(time[11:13])
    s=int(time[13:15])
    time=dt.datetime(y,m,d,h,mi,s)
    return time
    
#Set up a suitable GeoJSON formatted dictionary for the results
results = {
	u'type': u'FeatureCollection',
	u'features': []
	}
	
#Alias the relevant bit
export_features = results['features']

#Loop through the commutes

for walk in range(len(commute_journeys)):

    reference_time = 0
	
	#Alias trackPoints
    trackPoints = commute_journeys[walk]['data']['trackPoints']
        
    for point in range(len(trackPoints)-1):
    	#Get lat and lon into the right format
    	#for geopy to take distances
    	from_loc = (trackPoints[point]['lat'],trackPoints[point]['lon'])
        to_loc = (trackPoints[point+1]['lat'],trackPoints[point+1]['lon'])
        
        #Use vincenty to determine the distance between the two locations
        distance = vincenty(from_loc, to_loc).meters
        
        #Use time_parser to extract the times from the Moves data
        from_time = time_parser(trackPoints[point]['time'])
        to_time = time_parser(trackPoints[point+1]['time'])
        #Find the time taken between the two locations
        time_taken = (to_time - from_time).total_seconds()
        #Fix the time taken if it =0
        if time_taken == 0:
            time_taken = 1
        
        reference_time += time_taken
        
        #Find the speed - this is given in m/s
        speed = distance/time_taken
        print speed
        
        #write the speed to the first trackPoint in the pair
        trackPoints[point]['speed']=speed
        trackPoints[point]['reference_time']=reference_time
    
    #Now we're looking to write to a GeoJSON file.
    for point in range(len(trackPoints)-1):
    	line_data = trackPoints[point]
    	line_data2 = trackPoints[point+1]
    	
    	#create a suitable GeoJSON object with the speed as a property
    	line = {
    				u'geometry': 
    					{
    						u'type':u'LineString',
    						u'coordinates': [[line_data['lon'], \
    						line_data['lat']],\
    						[line_data2['lon'],line_data2['lat']]]
    					}, 
    				u'type': u'Feature',
    				u'properties':
    					{
    					u'speed': line_data['speed']
    					}
    			}
    	
    	#Append this object to the list
    	export_features.append(line)

#Save everything to a file
export_file = open('export_file.json','w')
json.dump(commute_journeys,export_file)
export_file.close()

#Convert all results to JSON
json_export_file = open('new_data.json','w')
json.dump(results,json_export_file)  
json_export_file.close()