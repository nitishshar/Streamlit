import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL=("MotorData.csv")
st.title("Motor Vehicle Collisions in NewYork City")
st.markdown("### This application is a streamlit dashboard that can used to analyse motor vehicles collision in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase=lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    print(list(data.columns.values))
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data

data = load_data(51000)
original_data=data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of Persons injured in Vehicle collisions",0,19)
st.map(data.query("number_of_persons_injured>=@injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of the day")
hour = st.slider("Hour To look at", 0,23)

data=data[data['date/time'].dt.hour==hour]
midpoint=(np.average(data['latitude']),np.average(data['longitude']))
st.markdown("Vehicle collision between %i:00 and %i:00" %(hour,(hour+1) %24))

st.write(pdk.Deck(
map_style="mapbox://styles/mapbox/light-v9",
initial_view_state={
"latitude":midpoint[0],
"longitude":midpoint[1],
"zoom":11,
"pitch":50
},
layers=[
pdk.Layer("HexagonLayer",
data=data[['date/time','longitude','latitude']],
get_position=['longitude','latitude'],
radius=100,
extruded=True,
pickable=True,
elevation_scale=4,
elevation_range=[0,1000]
),
]

))

st.subheader("Breakdown of collisions per minute between %i:00 and %i:00" % (hour,(hour+1)%24))
filtered= data[(data['date/time'].dt.hour>=hour) & (data['date/time'].dt.hour<(hour+1))]
hist=np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({'minute':range(60),'crashes':hist})

fig=px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.header("Top 5 dangerous street by affected type")
select=st.selectbox('Affected Typeof People',['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("number_of_pedestrians_injured>=1")[["on_street_name",'number_of_pedestrians_injured']].sort_values(by=['number_of_pedestrians_injured'],ascending=False).dropna(how='any')[:5])


elif select == 'Cyclists':
    st.write(original_data.query("number_of_cyclist_injured>=1")[["on_street_name",'number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'],ascending=False).dropna(how='any')[:5])
elif select == 'Motorists':
    st.write(original_data.query("number_of_motorist_injured>=1")[["on_street_name",'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'],ascending=False).dropna(how='any')[:5])

st.write(fig)
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)