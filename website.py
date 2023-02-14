import streamlit as st
import pandas as pd
import numpy as np
from assignment import pcu
from io import BytesIO
from PIL import Image
from zipfile import ZipFile

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def readfile(uploaded_file):
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file)
        return dataframe

def readfile_1(uploaded_file):
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file,usecols="B:E")
        return dataframe

rad = st.sidebar.radio("Navigation", ["About", "How to use app?", "Upload data"])

if rad == "About":
    st.title("About")
    st.write("The term ‘Passenger Car Unit (PCU)’, used in transportation engineering, is a metric that is used to measure the rate of traffic flow on a highway.  \n\nThe term PCU was first defined by the **Highway Capacity Manual** in 1965, as “The number of passenger cars displaced in the traffic flow by a truck or a bus, under prevailing roadway and traffic conditions”. In other words, the PCU can be referred to as a measure of the impact that a mode of transport has on a traffic variable, with reference to the impact of passenger cars.  \n\nThis helps us to gauge the various mix of vehicles that ply on a highway, such as trucks, buses, recreational vehicles, motorcycles, etc., in addition to the conventional passenger cars that we use. As this classification of vehicles is of prime importance to various studies and analyses by transportation engineers, ‘PCU’ is an essential metric that is to be measured.  \n\nThe typical ‘PCU’ values that are assigned to various categories of vehicles are as follows:  \n\n ")

    left, right = st.columns(2)
    img = Image.open('bigcar.png')
    left.image(img, width=300, caption="PCU value : 1.5")
    img = Image.open('car.png')
    right.image(img, width=300, caption="PCU value : 1.0")

    left1, right1 = st.columns(2)
    img = Image.open('2wheeler.png')
    left1.image(img, width=300, caption="PCU value : 0.75")
    img = Image.open('lcv.png')
    right1.image(img, width=300, caption="PCU value : 2.0")

    left2, right2 = st.columns(2)
    img = Image.open('bus.png')
    left2.image(img, width=300, caption="PCU value : 3.7")
    img = Image.open('truck.png')
    right2.image(img, width=300, caption="PCU value : 3.7")

    st.header("Objective")
    st.write("The objective of this application is to estimate the Dynamic PCU, from the input files provided by the user, and provide the output of the Dynamic PCU, in the time intervals, as specified by the user.")
    st.write("One of the popular techniques that is currently in use is the Chandra’s method, which was proposed by **Professor Satish Chandra**, affiliated to the **Indian Institute of Technology, Roorkee**. This method uses two factors for computing the PCU values:")
    st.markdown("- The velocity of vehicle type.")
    st.markdown("- Projected rectangular area.")
    st.markdown('''
    <style>
    [data-testid="stMarkdownContainer"] ul{
        padding-left:40px;
    }
    </style>
    ''', unsafe_allow_html=True)
    st.write("The formulation of PCU using Chandra’s method is as follows:")
    r'''
    $$(PCU)_i = \frac{(V_c/V_i)}{(A_c/A_i)}$$
    '''
    r'''where
    $$V_c$$ and $$V_i$$
     are the mean speeds of the car and vehicle of type ‘i’ respectively, and 
    $$A_c$$ and $$A_i$$
     are their respective projected rectangular area, that is (length * width) on the road.
    '''
    st.markdown("So, let's get started. :sunglasses:")
    

if rad == "How to use app?":
    st.title(rad)
    st.write("You should upload the field data and the area values of the vehicles as two separate .xlsx files.")
    st.write("The distance should be entered for which the data is measured.")
    st.write("Choose the time interval for which you want the PCU values be calculated for all vehicles.")
    df = readfile_1('sample.xlsx')
    st.write("The format of the data should be as follows:")
    st.table(df)
    st.write("The labels of the vehicle type should be as follows:")
    df = pd.DataFrame({
        "Vehicle type": ["SmallCar", "BigCar", "TwoWheeler", "LCV", "Bus", "SingleAxle", "MultiAxle"],
        "label" : [1, 2, 3, 4, 5, 6, 7]
    })
    st.table(df)
    st.warning(' Keep format as specified above.')


if rad == "Upload data":
    st.title(rad)
    
    uploaded_file1=st.file_uploader("Upload Field data file.", type=["xlsx"], accept_multiple_files=False)
    dataframe1 = readfile_1(uploaded_file1)
    uploaded_file2=st.file_uploader("Upload Area values file.", type=["xlsx"], accept_multiple_files=False)
    dataframe2 = readfile(uploaded_file2)

    distance_value, distance_type = st.columns([4, 2])

    with distance_type:
        dist_type = distance_type.selectbox("Choose the unit of distance.",('m', 'km'))
    with distance_value:    
        dist_value = distance_value.number_input("Enter distance value.", value=5)

    time_value, time_type= st.columns([4, 2])
    with time_type:
        t_type = time_type.selectbox("Choose the time unit.",('hr', 'min', 'sec'), index=1)
    with time_value:    
        t_value = time_value.number_input("Enter time value.", value=5)   

    click  = st.button("Submit Form")    
    
    if(click):
        if t_type == 'min':
            t_value = t_value*60
        if t_type == 'hr':
            t_value = t_value*60*60

        if dist_type == 'km':
            dist_value = dist_value*1000        
           
        df, df2 = pcu(dataframe1, dataframe2, dist_value, t_value)
        
        df.to_excel("pcu.xlsx")
        df2.to_excel("data.xlsx")

        st.write("The average values of PCU for the vehicles in the given interval are as follows:")
        st.table(df)

        with ZipFile('results.zip', 'w') as zip:
            zip.write('graph.png')
            zip.write("pcu.xlsx")
            zip.write("data.xlsx")

        st.write("Follwing are the calculations involved in getting PCU values:")
        st.dataframe(df2)
        
        with open("results.zip", "rb") as fp:
            st.download_button(
                label="Download as zip file",
                data=fp,
                file_name="results.zip",
                mime="application/zip"
            )

