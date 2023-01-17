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
# From D3D-FLOW result, export depth average at a specified location as .csv file using QUICKPLOT
# From D3D-FLOW result, exportw water level at a specified location as .csv file using QUICKPLOT
# Change the location & vertical_layer, start_date & end_date in Main block
# Plot all distance starting from origin
# Plot progressive vector diagram - assuming that the velocity around the location of interest does not change
# =============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import os
from shapely.geometry import LineString

#%% Function to import results
def ReadRawDataHorizontalVelocity(station, layer):
    data = pd.read_csv('horizontal velocity-all-layer-' + station + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    selected_data = data[data.columns[data.columns.str.contains(layer)]].iloc[:,0:2] #For each layer, there are 2 columns -> iloc 2 columns
    selected_data.columns = ['Velocity x', 'Velocity y']
    return selected_data
    
#%% Function to import results
def ReadRawDepthAverage(parameter, station):
    data = pd.read_csv(parameter + '-' + station + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    data.columns = ['Velocity x', 'Velocity y']
    return data

#%% Function to import results
def ReadRawWaterLevel(parameter, station):
    data = pd.read_csv(parameter + '-' + station + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    data.columns = ['water level (m)']
    return data

#%% Function to import results
def CalculateDistance(data, data_interval):
    # data_interval = (data.index[1] - data.index[0]).total_seconds()
    data['Distance x'] = data['Velocity x'] * data_interval
    data['Distance y'] = data['Velocity y'] * data_interval
    return data

#%% Main block
directory = r'C:\Users\baongoc.thai\OneDrive - Hydroinformatics Institute Pte Ltd\Desktop\Work\3. SFA APPS\d49e1_aprjun2017'
os.chdir(directory)
location = ['CYR','ECP','JIA','SJ1','SJ3','SJ4','SJ7','SJ8','SJ10','TUA']
vertical_layer = ['layer 1'] 

duration_second = 10/60 * 3600   #e.g., 10/60 = 10 minutes - depend on interval of D3D-FLOW outputs
start_date = '2017-04-20 00:00:00'
end_date = '2017-04-21 00:00:00'

#Read water level data
parameter = 'water level'
all_data_waterlevel = []
for i in range(len(location)):
    WaterLevel = ReadRawWaterLevel(parameter, location[i])
    # WaterLevel = WaterLevel.resample('H').mean()    
    all_data_waterlevel.append(WaterLevel)

#Read data & calculate distance
parameter = 'depth averaged velocity'
all_data_depth_average = []
for i in range(len(location)):
    DepthAverage = ReadRawDepthAverage(parameter,location[i])
    DepthAverage = CalculateDistance(DepthAverage, duration_second)
    DepthAverage['Water level (m)'] = all_data_waterlevel[i]['water level (m)']
    all_data_depth_average.append(DepthAverage)

all_data_layer1 = []
for i in range(len(location)):
    Layer1 = ReadRawDataHorizontalVelocity(location[i],vertical_layer[0])
    Layer1 = CalculateDistance(Layer1, duration_second)
    Layer1['Water level (m)'] = all_data_waterlevel[i]['water level (m)']
    all_data_layer1.append(Layer1)
    
#%% Plot progressive vector diagrams
# Plot for depth average
selected_data = all_data_depth_average
origin = (0, 0)
for i in range(len(selected_data)):
    selected_data[i] = selected_data[i][start_date:end_date]
    for j in range(len(selected_data[i]['Distance x'])):
        x1 = origin[0] + selected_data[i]['Distance x'][j]  #Calculation for progressive diagram
        y1 = origin[1] + selected_data[i]['Distance y'][j]  #Calculation for progressive diagram
        line = LineString([origin, (x1, y1)])
        x2, y2 = line.xy
        plt.plot(0, 0, x2, y2)
        origin = (x2[1], y2[1])
        # if j == 10: break
    plt.plot(0,0, ".", color='black', markersize=10)
    plt.rcParams.update({'font.size': 12})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title(location[i] + ' - DepthAverage ('+ 
              str(pd.to_datetime(start_date))+ ' to '+str(pd.to_datetime(end_date))+')',size=12)
    plt.xlabel('East-West movement (m)')
    plt.ylabel('North-South movement (m)')
    plt.axis('square')
    plt.savefig("ProgressiveVectorDiagram\\"+location[i]+'_DepthAverage_After '+ str(duration_second) + ' s ('+
                str(pd.to_datetime(start_date).date())+ ' to '+str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    plt.close()
    print (location[i])
    origin = (0, 0)
    
# Plot for surface layer 1
selected_data = all_data_layer1
origin = (0, 0)
for i in range(len(selected_data)):
    selected_data[i] = selected_data[i][start_date:end_date]
    for j in range(len(selected_data[i]['Distance x'])):
        x1 = origin[0] + selected_data[i]['Distance x'][j]  #Calculation for progressive diagram
        y1 = origin[1] + selected_data[i]['Distance y'][j]  #Calculation for progressive diagram
        line = LineString([origin, (x1, y1)])
        x2, y2 = line.xy
        plt.plot(0, 0, x2, y2)
        origin = (x2[1], y2[1])
    plt.plot(0,0, ".", color='black', markersize=10)
    plt.rcParams.update({'font.size': 12})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title(location[i] + ' - '+ vertical_layer[0] + ' (' +
              str(pd.to_datetime(start_date))+ ' to '+str(pd.to_datetime(end_date))+')',size=12)
    plt.xlabel('East-West movement (m)')
    plt.ylabel('North-South movement (m)')
    plt.axis('square')
    plt.savefig("ProgressiveVectorDiagram\\"+location[i]+'_'+vertical_layer[0]+'_'+'After '+ str(duration_second) + ' s ('+
                str(pd.to_datetime(start_date).date())+ ' to '+str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    plt.close()
    print (location[i])
    origin = (0, 0)

#%% Plot lines starting from origin
# Plot for depth average
origin = (0, 0)
for i in range(len(all_data_depth_average)):
    for j in range(len(all_data_depth_average[i]['Distance x'])):
        x1 = all_data_depth_average[i]['Distance x'][j]
        y1 = all_data_depth_average[i]['Distance y'][j]
        line = LineString([origin, (x1, y1)])
        x2, y2 = line.xy
        plt.plot(0, 0, x2, y2)
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title(location[i] + ' - DepthAverage - after '+ str(duration_second) + ' s ('+
              str(pd.to_datetime(start_date))+ ' to '+str(pd.to_datetime(end_date))+')')
    plt.xlabel('Distance x-direction (m)')
    plt.ylabel('Distance y-direction (m)')
    plt.savefig("DistancePlot\\"+location[i]+'_DepthAverage_After'+ str(duration_second) + ' s ('+
                str(pd.to_datetime(start_date).date())+ ' to '+str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    plt.close()
    print (location[i])

# Plot for surface layer 1
origin = (0, 0)
for i in range(len(all_data_layer1)):
    for j in range(len(all_data_layer1[i]['Distance x'])):
        x1 = all_data_layer1[i]['Distance x'][j]
        y1 = all_data_layer1[i]['Distance y'][j]
        line = LineString([origin, (x1, y1)])
        x2, y2 = line.xy
        plt.plot(0, 0, x2, y2)
    
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title(location[i] + ' - '+ vertical_layer[0] + ' after '+ str(duration_second) + ' s ('+
              str(pd.to_datetime(start_date))+ ' to '+str(pd.to_datetime(end_date))+')')
    plt.xlabel('Distance x-direction (m)')
    plt.ylabel('Distance y-direction (m)')
    plt.savefig("DistancePlot\\"+location[i]+'_'+vertical_layer[0]+'_'+'After'+ str(duration_second) + ' s ('+
                str(pd.to_datetime(start_date).date())+ ' to '+str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    plt.close()
    print (location[i])
    
    
#%% Plot water level
selected_data = all_data_waterlevel
for i in range(len(selected_data)):
    selected_data[i] = selected_data[i][start_date:end_date]
    plt.plot(selected_data[i].index, selected_data[i]['water level (m)'])
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title('Water Level (m) at ' + location[i])
    plt.ylabel('Water level (m)')
    plt.xlim(selected_data[i].index[0].date(), selected_data[i].index[-1].date())
    plt.savefig("WaterLevel\\"+location[i]+' ('+str(pd.to_datetime(start_date).date())+ ' to '+
                str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    print (location[i])
    plt.close()

