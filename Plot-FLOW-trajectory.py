# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 16:04:25 2023

@author: baongoc.thai
"""

# =============================================================================
# This script plots the trajectory of water from the specified origin (location & vertical layer)
# up to the estimated distance based on specified duration and velocity (m/s)
# This is to estimate the horizontal mixing length at a point of observation
# From D3D-FLOW result, export horizontal velocity at all layer at a specified location as .csv file using QUICKPLOT
# From D3D-FLOW result, export depth average at all layer at a specified location as .csv file using QUICKPLOT
# Change the location & vertical_layer in Main block
# =============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import os
from shapely.geometry import LineString

#%% Function to import results
def ReadRawDataHorizontalVelocity(station, layer):
    data = pd.read_csv('horizontal velocity-all-layer-' + location + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    selected_data = data[data.columns[data.columns.str.contains(layer)]].iloc[:,0:2] #For each layer, there are 2 columns -> iloc 2 columns
    selected_data.columns = ['Velocity x', 'Velocity y']
    return selected_data
    
#%% Function to import results
def ReadRawDataDepthAverage(station):
    data = pd.read_csv('depth averaged velocity-' + location + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    data.columns = ['Velocity x', 'Velocity y']
    return data

#%% Function to import results
def CalculateDistance(data):
    data_interval = (data.index[1] - data.index[0]).total_seconds()
    data['Distance x'] = data['Velocity x'] * data_interval
    data['Distance y'] = data['Velocity y'] * data_interval
    return data

#%% Main block
directory = r'C:\Users\baongoc.thai\OneDrive - Hydroinformatics Institute Pte Ltd\Desktop\Work\3. SFA APPS\d49e1_aprjun2017'
os.chdir(directory)
location = 'TUA'
vertical_layer = ['layer 1'] 
duration_hour = 1   #Choose 1hr because WAQ results interval is 1hr

#Read data & calculate distance
DepthAverage = ReadRawDataDepthAverage(location)
DepthAverage = CalculateDistance(DepthAverage)

Layer1 = ReadRawDataHorizontalVelocity(location,vertical_layer[0])
Layer1 = CalculateDistance(Layer1)

# Plot for depth average
origin = (0, 0)
for j in range(len(DepthAverage['Distance x'])):
    x1 = DepthAverage['Distance x'][j]
    y1 = DepthAverage['Distance y'][j]
    line = LineString([origin, (x1, y1)])
    x2, y2 = line.xy
    plt.plot(0, 0, x2, y2)

plt.rcParams.update({'font.size': 15})
plt.tight_layout()
figure = plt.gcf()
figure.set_size_inches(18, 6)
plt.title(location + ' - DepthAverage - after '+ str(duration_hour) + ' hour')
plt.xlabel('Distance x-direction (m)')
plt.ylabel('Distance y-direction (m)')
plt.savefig("DistancePlot\\"+location+'_DepthAverage_After1hour'+'.png', bbox_inches='tight',dpi=600)
plt.close()
print (location)

# Plot for surface layer 1
origin = (0, 0)
for j in range(len(Layer1['Distance x'])):
    x1 = Layer1['Distance x'][j]
    y1 = Layer1['Distance y'][j]
    line = LineString([origin, (x1, y1)])
    x2, y2 = line.xy
    plt.plot(0, 0, x2, y2)

plt.rcParams.update({'font.size': 15})
plt.tight_layout()
figure = plt.gcf()
figure.set_size_inches(18, 6)
plt.title(location + ' - '+ vertical_layer[0] + ' after '+ str(duration_hour) + ' hour')
plt.xlabel('Distance x-direction (m)')
plt.ylabel('Distance y-direction (m)')
plt.savefig("DistancePlot\\"+location+'_'+vertical_layer[0]+'_'+'After1hour'+'.png', bbox_inches='tight',dpi=600)
plt.close()
print (location)

