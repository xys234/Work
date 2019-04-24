
# coding: utf-8

# In[81]:


import googlemaps
import json
from datetime import datetime
import time
import calendar
import csv
import math
import urllib


# In[24]:


gmaps = googlemaps.Client(key='')

# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')


# In[15]:


# Specifies the desired time of departure. 
# As an integer in seconds since midnight, January 1, 1970 UTC.
times_str = ['May 12 8:00:00 2019']
times = [time.strptime(t, '%b %d %H:%M:%S %Y') for t in times_str] 
times_utc = [calendar.timegm(t) for t in times]
departure_time = times_utc[0]


# ### Distance Matrix API

# In[4]:


# Destination
addresses = [
    ('Branch Avenue', '4704 Old Soper Road, Suitland, MD 20746')
]
add = [a for (n, a) in addresses]


# In[63]:


# read in the zone centroids as destinations
zones = []
with open(r"../data/origins.csv", 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    i = 0
    for row in reader:
        if (i>0):
            zones.append((int(row[0]), float(row[2]), float(row[1]))) # id, long, lat
        i += 1
z = [(lat, long) for (i, long, lat) in zones]


# In[64]:


z


# In[12]:


def parse_distance_matrix(distance_matrix):
    '''
    Input:
    distance_matrix: distance matrix returned by Google Distance Matrix API. 
    For this application, the matrix contains distance from multiple origins to a single destination

    
    Output:
    distances   : a list contains the distance
    travel_times: a list contains the travel times
    '''
    # Get the matrix dimensions
    n_orig = len(distance_matrix['rows'])
    n_dest = len(distance_matrix['rows'][0]['elements'])
    
    distances = [0]*n_orig
    travel_times = [0]*n_orig
    
    for i in range(n_orig):
        data = distance_matrix['rows'][i]['elements']  # a list n to 1 destination       
        distances[i] = [round(k['distance']['value']/1600.0, 2) if k['status'] == "OK" else k['status'] for k in data]   # meters to miles
        travel_times[i] = [round(k['duration']['value']/60.0, 2) if k['status'] == "OK" else k['status'] for k in data]
    return distances, travel_times


# In[13]:


def batch_process(gmaps, origins, destinations, departure_time, traffic_model='pessimistic', units='imperial', batch_size = 10):
    '''
        Process the API requests by small batches assuming many origins, i.e. batching by origins
    '''
    
    n_orig = len(origins)
    n_dest = len(destinations)
    
    index = list(range(0, len(origins), batch_size))
    if (index[-1] != len(origins)):
        index.append(len(origins))
    
    matrices = [0]*(len(index)-1)
    distances = [0]*(len(index)-1)
    travel_times = [0]*(len(index)-1)
    
    for k in range(1, len(index)):
        og = origins[index[k-1]:index[k]]
        print("Processing Locations {0:d} to {1:d}".format(index[k-1]+1, index[k]))
        distance_matrix = gmaps.distance_matrix(og, destinations, 
                                               departure_time=departure_time, 
                                               traffic_model=traffic_model, units=units)
        print("Finish retrieving matrix")
        matrices[k-1] = distance_matrix
        d, t = parse_distance_matrix(distance_matrix)
        distances[k-1], travel_times[k-1] = d, t
    return distances, travel_times, matrices


# In[59]:


distances, travel_times, matrices = batch_process(gmaps, z, add, departure_time=departure_time, batch_size = 1)


# In[60]:


l = [item[0] for sublist in distances for item in sublist]
t = [item[0] for sublist in travel_times for item in sublist]
with open(r'..\data\Travel_times.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["ID", "Long", "Lat", "Distance", "Time"])
    for zi, dist, time in zip(zones, l, t):
        writer.writerow([zi[0], zi[1], zi[2], dist, time])

