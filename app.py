import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    "motor_vehicle_collisions.csv")
st.title("Motor vehicle collisions in new york city")
st.markdown("This application is a "
            "Streamlit Dashboard that is used to analyze moter vehicle collsisions in new york")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[
        ['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    def lowercase(x): return str(x).lower().strip()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash date_crash time': 'date_time'}, inplace=True)

    return data


data = load_data(100000)

# copy of original dataframe with all records
original_data = data


st.header('Where are the most people injured in New york city')
injured_people = st.slider(
    "Number of persons injured in  vehicle collisions", 0, 19)
st.map(data[data['number of persons injured'] >= injured_people]
       [['latitude', 'longitude']].dropna(how="any"))

st.header('How many collisions occured during a given time of day?')
hour = st.slider('Hour to look at', 0, 23)
data = data[data['date_time'].dt.hour == hour]


st.markdown('Vehicle colissions between %i.00 and %i.00' %
            (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date_time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],

        )
    ]

))


st.subheader("breakdown by minute between %i.00 and %i.00" %
             (hour, (hour+1) % 24))
filtered = data[
    (data['date_time'].dt.hour >= hour) & (
        data['date_time'].dt.hour < (hour + 1))
]

hist = np.histogram(filtered['date_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes',
             hover_data=['minute', 'crashes'], height=400)

st.write(fig)
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', [
                      'Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data[original_data['number of pedestrians injured'] >= 1]
             [["on street name", 'number of pedestrians injured']]
             .sort_values(by=['number of pedestrians injured'], ascending=False)
             .dropna(how="any")[:5])


elif select == 'Cyclists':
    st.write(original_data[original_data['number of cyclist injured'] >= 1]
             [["on street name", 'number of cyclist injured']]
             .sort_values(by=['number of cyclist injured'], ascending=False)
             .dropna(how="any")[:5])


else:
    st.write(original_data[original_data['number of motorist injured'] >= 1]
             [["on street name", 'number of motorist injured']]
             .sort_values(by=['number of motorist injured'], ascending=False)
             .dropna(how="any")[:5])


#if st.checkbox('Show rae data', False):
    #st.subheader('RAW DATA')
    #st.write(data)
