import numpy as np
import pandas as pd
import math
import streamlit as st
import matplotlib.pyplot as plt
from scipy.optimize import minimize, curve_fit

def objective(x, a, b, c):
    return a * x**2 + b * x + c

def pcu(data, area, dist, tim):
    # df = pd.read_excel(data, usecols='B:E')
    df = data
    df = df.dropna()

    df['travel_time']=df['Time Stamp Exit']-df['Time Stamp Entry']
    # st.write(distance)
    df['speed'] = dist/(df['Time Stamp Exit']-df['Time Stamp Entry'] )*18/5

    max_time = df['Time Stamp Exit'].max()
    print(max_time)
    print((max_time/tim))
    num_interval = math.ceil(max_time/tim)
    time_interval=[]
    for i in range(1,num_interval+1):
        time_interval.append(i*tim)
    # time_interval
    df_interval = pd.DataFrame(time_interval,columns=['time_interval'])

    temp = [tim * i for i in range(num_interval + 1)]


    df.groupby(pd.cut(df['Time Stamp Entry'],temp))

    df_interval['EntryFlowPInterval']= df.groupby(pd.cut(df['Time Stamp Entry'],temp)).count()['Lane'].values
    df_interval['ExitFlowPInterval']= df.groupby(pd.cut(df['Time Stamp Exit'],temp)).count()['Lane'].values

    df_interval['totalTravelTimePMin'] =  df.groupby(pd.cut(df['Time Stamp Exit'],temp)).sum()['travel_time'].values
    df_interval['avgTravelTimePMin'] = df_interval['totalTravelTimePMin']/df_interval['ExitFlowPInterval']
    df_interval['SMS']=dist/df_interval['avgTravelTimePMin']*3.6
    df_interval['exitFlowPHour'] = np.floor(3600*df_interval['ExitFlowPInterval']/tim)
    df_interval["density"] = df_interval["exitFlowPHour"]/df_interval["SMS"]

    # pd.DataFrame(df.groupby(pd.cut(df['Time Stamp Exit'],temp))["Vehicle Type"].value_counts())
    df1 = df
    index_map = pd.DataFrame(df1.groupby([pd.cut(df1['Time Stamp Exit'],temp), "Vehicle Type"], as_index=False)["Lane"].count().groupby("Vehicle Type")).to_dict()[0]
    type_map = {}
    i=1
    for k in index_map:
        if index_map[k]!=i:
            type_map[i]=-1
            i=i-1
        type_map[index_map[k]] = k
        i=i+1
    
    vec_type = {1.0:"SmallCar",2.0:"BigCar",3.0:"TwoWheeler",4.0:"LCV",5.0:"Bus",6.0:"SingleAxle",7.0:"MultiAxle"}

    for k in type_map:
        if type_map[k]!=-1:
            df_interval[vec_type[k]]=pd.DataFrame(df1.groupby([pd.cut(df1['Time Stamp Exit'],temp), "Vehicle Type"], as_index=False)["Lane"].count().groupby("Vehicle Type")).to_dict()[1][type_map[k]].reset_index()["Lane"]

    for k in type_map:
        if type_map[k]!=-1:
            df_interval[vec_type[k]+"Speed"]=pd.DataFrame(df1.groupby([pd.cut(df1['Time Stamp Exit'],temp), "Vehicle Type"], as_index=False)["speed"].sum().groupby("Vehicle Type")).to_dict()[1][type_map[k]].reset_index()["speed"]

    for k in type_map:
        if type_map[k]!=-1:
            df_interval[vec_type[k]+"AverageSpeed"]=df_interval[vec_type[k]+"Speed"] / df_interval[vec_type[k]]

    areaValues = area
    areaValues = areaValues.dropna()

    areaValues.set_index("Category", inplace=True)

    for k in type_map:
        if type_map[k]!=-1:
            df_interval["PCU"+vec_type[k]]=(df_interval["SmallCarAverageSpeed"]/df_interval[vec_type[k]+"AverageSpeed"])/(areaValues.at["SmallCar", "Area"]/areaValues.at[vec_type[k], "Area"])

    meanPCU={}
    for k in type_map:
        if type_map[k]!=-1:
            list=[]
            list.append(df_interval["PCU"+vec_type[k]].mean())
            meanPCU["PCU"+vec_type[k]]=list
    df_result = pd.DataFrame(meanPCU)

    fig = plt.figure()
    plt.scatter(df_interval["density"], df_interval["exitFlowPHour"])
    popt, _ = curve_fit(objective, df_interval["density"], df_interval["exitFlowPHour"], bounds = ((-120, -120, -120), (120, 120, 120)))
    a, b, c = popt
    if b**2-4*a*c >= 0 :
        mx = max(((-b+math.sqrt(b**2 - 4*a*c))/(2*a)),(-b-math.sqrt(b**2 - 4*a*c))/(2*a))
    else:
        mx = 150
        st.error("Invalid data! Please upload valid data files.") 
    x_line = np.arange(0, mx, 1)
    y_line = objective(x_line, a, b, c)
    
    plt.plot(x_line, y_line, '--', color='red')
    plt.title("Flow Density curve")
    plt.xlabel("Density (pcu per km)")
    plt.ylabel("Flow rate (pcu per hour)")
    st.write(fig)
    plt.savefig("graph.png")
    df_interval.fillna(value=0, inplace=True)
    return df_result, df_interval
