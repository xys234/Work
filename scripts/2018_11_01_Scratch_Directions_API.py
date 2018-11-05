
# coding: utf-8

# In[4]:


import googlemaps
from datetime import datetime
import time
import calendar
import csv


# In[5]:


gmaps = googlemaps.Client(key='AIzaSyB6G2u6Iq7MVRqjt6cyYX38aM3rI7iAx0M')


# In[6]:


# Specifies the desired time of departure. 
# As an integer in seconds since midnight, January 1, 1970 UTC.
times_str = ['May 12 8:00:00 2019']
times = [time.strptime(t, '%b %d %H:%M:%S %Y') for t in times_str] 
times_utc = [calendar.timegm(t) for t in times]
departure_time = times_utc[0]


# In[8]:


# read in the zone centroids as destinations
zones = []
with open(r"../data/origins.csv", 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    i = 0
    for row in reader:
        if (i>0):
            zones.append((float(row[1]), float(row[2]))) # id, long, lat
        i += 1
zones


# In[17]:


# Destination
addresses = [
    '4704 Old Soper Road, Suitland, MD 20746'
] * len(zones)
addresses


# ### Direction API

# In[20]:


def parse_directions_result(directions_result):
    '''
    parse the returned json to get distance, duration_in_traffic, start_address, end_address, summary (main road)
    
    '''
    
    if directions_result:
        
        distance = round(directions_result[0]['legs'][0]['distance']['value']/1600.0, 1)      # value field always in meters
        travel_time = round(directions_result[0]['legs'][0]['duration_in_traffic']['value']/60.0, 2) # always in seconds
        
        return distance, travel_time,                directions_result[0]['legs'][0]['start_address'],  directions_result[0]['legs'][0]['end_address'],                directions_result[0]['summary']
    else:
        return -1, -1, None, None, None
    


# In[21]:


def batch_processing(gmaps, origins, destinations, departure_time=None, batch_size=50, delay=60, verbose=10):
    """
    batch process the direction requests.
    
    :param gmaps:  a gmap client 
    :type  gmaps:  a gmap client
    
    :param origins:  a list of origins in lat/long tuples or text addresses
    :type  origins:  list
    
    :param destinations:  a list of destinations in lat/long tuples or text addresses
    :type  destinations:  list
    
    :param departure_time:  departure time in utc
    :type  departure_time:  int
    
    :param delay:  wait time in seconds for batch_size requests
    :type  delay:  int

    :param verbose:  print a status message for every "verbose" requests 
    :type  verbose:  int
    
    """
    
    if len(origins) != len(destinations):
        raise Exception('Number of origins and destinations must be the same.')
    batch_size = min(batch_size, len(origins))
    
    if departure_time is None:
        departure_time = datetime.utcnow()
    
    results = []
    for i, (o, d) in enumerate(zip(origins, destinations)):
        if i > 0 and i % batch_size == 0:
            print('Waiting {0:d} seconds before continuing.'.format(delay))
            time.sleep(delay)
            
        if i % verbose == 0 or i == len(origins) - 1:
            print("Processing OD pair {0:d}".format(i+1))
        direction = gmaps.directions(o, d, mode="driving", departure_time=departure_time) 
        distance, duration_in_traffic, start_address, end_address, summary = parse_directions_result(direction)
        results.append((distance, duration_in_traffic, start_address, end_address, summary))
    return results


# In[22]:


# test the current departure time
results_depart_now = batch_processing(gmaps, zones, addresses)


# In[23]:


results_depart_now


# In[25]:


results_depart_future = batch_processing(gmaps, zones, addresses, departure_time=departure_time)
results_depart_future


# In[113]:


# test the delay, need to comment out the API call
a, b = range(20), range(20)
batch_processing(gmaps, a, b, batch_size=5, delay=2)


# In[27]:


with open(r'..\data\Travel_times.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["OD", "Distance", "Time", "Start_Address", "End_Address", "Main Leg"])
    for i, d in enumerate(results_depart_future):
        writer.writerow([i, *d])

