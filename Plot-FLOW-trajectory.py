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
# Convert distance to next co-ordinate: https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters
# =============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import os
from shapely.geometry import LineString
import math

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
def ReadParameter(parameter, station, layer):    
    data = pd.read_csv(parameter + '-' + station + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')
    selected_data = data[data.columns[data.columns.str.contains(layer)]].iloc[:,0:1]    #Only surfacelayer
    return selected_data

#%% Function to import results
def ReadRawWaterLevel(parameter, station):
    data = pd.read_csv(parameter + '-' + station + '.csv')
    data['date and time'] = pd.to_datetime(data['date and time'], format='%Y-%m-%d %H:%M:%S')
    data.index = data.pop('date and time')    
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
location = ['CYR','ECP','JIA','SJ1','SJ3','SJ4','SJ7','SJ8','SJ10','TUA','PP','TP','StJ','PSe','mpa_rl','CHG']
# location = ['CHG', 'TUA']
vertical_layer = ['layer 1'] 

duration_second = 10/60 * 3600   #e.g., 10/60 = 10 minutes - depend on interval of D3D-FLOW outputs
start_date = '2017-04-20 00:00:00'
end_date = '2017-04-21 00:00:00'

#Read observation locations
Obs_location = pd.read_csv('Observation points locations.csv')
Obs_location.index = Obs_location.pop('Station')

#Read water level data
parameter = 'water level'
all_data_waterlevel = []
for i in range(len(location)):
    WaterLevel = ReadRawWaterLevel(parameter, location[i])
    WaterLevel.rename(columns={ WaterLevel.columns[0]: "water level (m)" }, inplace = True)
    all_data_waterlevel.append(WaterLevel)
    
#Read salinity data
parameter = 'salinity'
all_data_salinity = []
for i in range(len(location)):
    Salinity = ReadParameter(parameter, location[i], vertical_layer[0])
    Salinity.rename(columns={ Salinity.columns[0]: "salinity (ppt)" }, inplace = True)
    all_data_salinity.append(Salinity)
    
#Read discharge data
parameter = 'discharge'
all_data_discharge = []
for i in range(len(location)):
    Discharge = ReadParameter(parameter, location[i], vertical_layer[0])
    Discharge.rename(columns={ Discharge.columns[0]: "discharge (m3/s)" }, inplace = True)
    all_data_discharge.append(Discharge)

#Read water depth data
parameter = 'water depth'
all_data_waterdepth = []
for i in range(len(location)):
    WaterDepth = ReadRawWaterLevel(parameter, location[i])
    WaterDepth.rename(columns={ WaterDepth.columns[0]: "water depth (m)" }, inplace = True)
    all_data_waterdepth.append(WaterDepth)

#Read data & calculate distance
parameter = 'depth averaged velocity'
all_data_depth_average = []
for i in range(len(location)):
    DepthAverage = ReadRawDepthAverage(parameter,location[i])
    DepthAverage = CalculateDistance(DepthAverage, duration_second)
    # DepthAverage['Water level (m)'] = all_data_waterlevel[i]['water level (m)']
    all_data_depth_average.append(DepthAverage)

all_data_layer1 = []
for i in range(len(location)):
    Layer1 = ReadRawDataHorizontalVelocity(location[i],vertical_layer[0])
    Layer1 = CalculateDistance(Layer1, duration_second)
    # Layer1['Water level (m)'] = all_data_waterlevel[i]['water level (m)']
    all_data_layer1.append(Layer1)
    
    
#%% Calculate next position
selected_data = all_data_depth_average
# origin = (103.65504, 1.2894661)
for i in range(len(selected_data)):
    origin = (Obs_location.loc[location[i]][0], Obs_location.loc[location[i]][1])   #Lon & Lat of observation points
    selected_data[i] = selected_data[i][start_date:end_date]
    selected_data[i]['Lat'] = origin[1]
    selected_data[i]['Lon'] = origin[0]
    for j in range(len(selected_data[i]['Distance x'])):
        selected_data[i]['Lat'][j+1] = selected_data[i]['Lat'][j] + selected_data[i]['Distance y'][j]/1000/6378*180/math.pi  #Calculation for progressive diagram
        selected_data[i]['Lon'][j+1] = selected_data[i]['Lon'][j] + selected_data[i]['Distance x'][j]/1000/6378*180/math.pi/math.cos(selected_data[i]['Lat'][j+1]*math.pi/180)  #Calculation for progressive diagram
        print(j)
        if j+1 >= (len(selected_data[i]['Distance x'])-1): 
            break
        if selected_data[i].index[j+1].date() != selected_data[i].index[j].date():
            selected_data[i]['Lat'][j+1] = origin[1]    #reset origin for the next day
            selected_data[i]['Lon'][j+1] = origin[0]
            j=j+1
        elif selected_data[i].index[j+1].date() == selected_data[i].index[j].date():  #same date to be plotted in the same trajectory
            continue

#Write file to csv
for i in range(len(selected_data)):
    filename = location[i] + '_' + str(pd.to_datetime(start_date).date()) + '-' + str(pd.to_datetime(end_date).date()) + '.csv'
    selected_data[i].to_csv('1-day Position\\' + filename)

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
        if j == (len(selected_data[i]['Distance x'])-1): break
        elif selected_data[i].index[j].date() == selected_data[i].index[j+1].date():  #same date to be plotted in the same trajectory
            origin = (x2[1], y2[1])
        else: origin = (0,0)    #reset origin for the next day
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
        if j == (len(selected_data[i]['Distance x'])-1): break
        elif selected_data[i].index[j].date() == selected_data[i].index[j+1].date():  #same date to be plotted in the same trajectory
            origin = (x2[1], y2[1])
        else: origin = (0,0)
    plt.plot(0,0, ".", color='black', markersize=10)
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
    plt.plot(selected_data[i].index, selected_data[i]['water level (m)'],label = location[i])
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title('Water Level (m) at ' + location[i])
    plt.ylabel('Water level (m)')
    plt.xlim(selected_data[i].index[0], selected_data[i].index[-1])
    plt.legend()
    plt.savefig(
        "WaterLevel\\"+
                location[i]+' ('+str(pd.to_datetime(start_date).date())+ ' to '+
                str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    print (location[i])
    plt.close()

#%% Plot Salinity
selected_data = all_data_salinity
for i in range(len(selected_data)):
    selected_data[i] = selected_data[i][start_date:end_date]
    plt.plot(selected_data[i].index, selected_data[i]['salinity (ppt)'],label = location[i])
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title('Salinity (ppt) at ' + location[i])
    plt.ylabel('Salinity (ppt)')
    plt.xlim(selected_data[i].index[0], selected_data[i].index[-1])
    plt.legend()
    plt.savefig(
        "WaterLevel\\"+
                location[i]+' ('+str(pd.to_datetime(start_date).date())+ ' to '+
                str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    print (location[i])
    plt.close()

#%% Plot Discharge
selected_data = all_data_discharge
for i in range(len(selected_data)):
    selected_data[i] = selected_data[i][start_date:end_date]
    plt.plot(selected_data[i].index, selected_data[i]['discharge (m3/s)'],label = location[i])
    plt.rcParams.update({'font.size': 15})
    plt.tight_layout()
    figure = plt.gcf()
    figure.set_size_inches(18, 6)
    plt.title('Discharge (m3/s) at ' + location[i])
    plt.ylabel('Discharge (m3/s)')
    plt.xlim(selected_data[i].index[0], selected_data[i].index[-1])
    plt.legend()
    plt.savefig(
        "WaterLevel\\"+
                location[i]+' ('+str(pd.to_datetime(start_date).date())+ ' to '+
                str(pd.to_datetime(end_date).date())+')'+'.png', bbox_inches='tight',dpi=600)
    print (location[i])
    plt.close()
    
#%% Water Depth
selected_data = all_data_waterdepth

mean_depth = []
for i in range(len(selected_data)):
    mean_depth.append(selected_data[i].mean()[0])
AverageDepth = pd.DataFrame(mean_depth, location)
AverageDepth.rename(columns={ AverageDepth.columns[0]: "average depth (m)" }, inplace = True)
AverageDepth.to_csv('Average depth (m) at selected locations.csv')

surface_layer = []
for i in range(len(selected_data)):
    selected_data[i]['layer 1 depth (m)'] = selected_data[i]['water depth (m)']/20 #20 signma layers
    surface_layer.append(selected_data[i].mean()[1])
SurfaceLayer = pd.DataFrame(surface_layer, location)
SurfaceLayer.rename(columns={ SurfaceLayer.columns[0]: "surface layer depth (m)" }, inplace = True)
SurfaceLayer.to_csv('Surface layer depth (m) at selected locations.csv')
