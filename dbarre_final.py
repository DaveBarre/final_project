"""
Name: David Barre
Class: CS 230
Data: volcanoes.csv
URL:
Description: This code provides the user the ability to view a bar chart, scatterplot, or map of the data.
The user has the ability to change the colors and markers of the charts and can edit which volcanoes to map/chart.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import csv
import pydeck as pdk


def page_1(df):
    # Display in streamlit and pick which region of volcano
    st.title("Volcanoes Bar Chart")
    option_columns = df["Region"].unique()
    data_selection = st.sidebar.selectbox("Select an region: ", option_columns)
    st.sidebar.write("Data Selection: ", data_selection)
    color = st.sidebar.color_picker('Pick a color')
    # Use dict and list to make x's and y's for graphs
    subregions = []
    sub_dict = {}
    all_dict = dict(df.groupby("Subregion")["Elevation (m)"].mean())
    with open('volcanoes.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            if row[6] == data_selection:
                for key, val in all_dict.items():
                    if row[7] == key:
                        sub_dict[key] = val
    for key in sub_dict:
        subregions.append(key)
    # Plot the values in a HORIZONTAL bar chart
    fig = plt.figure()
    x = subregions
    y = sub_dict.values()
    plt.ylabel("Subregions")
    plt.xlabel("Mean Elevation (In Meters)")
    plt.barh(x, y, color=color)
    st.write(fig)
    return plt


def page_2(df):
    st.title("Volcanoes ScatterPlot")
    data_selection = st.sidebar.selectbox("Select an type of volcano: ", vol_type)
    # Print data on sidebar of streamlit
    num = df[df['Primary Volcano Type'] == data_selection]['Last Known Eruption'].count()
    st.sidebar.write(f"Number of points plotted: {num}")
    mean_ele = df[df['Primary Volcano Type'] == data_selection]['Elevation (m)'].mean()
    st.sidebar.write(f"Average Elevation of {data_selection}: {mean_ele:.2f}")
    mean_date = df[df['Primary Volcano Type'] == data_selection]['Last Known Eruption'].mean()
    st.sidebar.write(f"Average of Last Known Eruption: {mean_date:.2f}")
    # Pick color and marker of scatterplot
    marker = st.sidebar.selectbox("Select the scatterplot marker style: ", ["x", "o", "^"])
    color = st.sidebar.color_picker('Pick a color')
    # Plot the scatter plot
    fig = plt.figure()
    df = df.loc[df['Primary Volcano Type'] == data_selection]
    x = df["Last Known Eruption"]
    y = df['Elevation (m)']
    plt.xlabel("Last Known Eruption (In Years)")
    plt.ylabel("Elevation (In Meters)")
    plt.scatter(x, y, marker=marker, color=color)
    st.write(fig)
    return plt


def page_3(df):
    data_selection = st.sidebar.selectbox("Select an type of volcano: ", vol_type)
    # Get max and min for slider
    max_ele = df[df['Primary Volcano Type'] == data_selection]['Last Known Eruption'].max()
    min_ele = df[df['Primary Volcano Type'] == data_selection]['Last Known Eruption'].min()
    max_ele = float(max_ele)
    min_ele = float(min_ele)
    value = st.sidebar.slider("Last Known Eruption: ", value=[max_ele, min_ele])
    max_choose = value[1]
    min_choose = value[0]
    # Sort data and rename columns
    df = df.loc[df['Primary Volcano Type'] == data_selection]
    df = df.loc[df["Last Known Eruption"] < max_choose]
    df = df.loc[df["Last Known Eruption"] > min_choose]
    df = pd.DataFrame(df, columns=['Volcano Name', 'Latitude', 'Longitude', 'Elevation (m)', 'Last Known Eruption'])
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.title("Volcanoes Map and Dataframe")
    # Print data frame with on certain columns
    df_print = pd.DataFrame(df, columns=['Volcano Name', 'Elevation (m)', 'Last Known Eruption'])
    st.dataframe(df_print.style.format({'Last Known Eruption': '{:,.0f}'.format}))
    # Give layers to map so different elevations will have different colors
    layer1 = pdk.Layer('ScatterplotLayer',
                    data=df.loc[df['Elevation (m)'] > 5000],
                  get_position='[lon, lat]',
                  get_radius=100000,
                  get_color=[255, 0, 0],   # Red
                  pickable=True)
    layer2 = pdk.Layer('ScatterplotLayer',
                  data=df.loc[df['Elevation (m)'] < 5000],
                  get_position='[lon, lat]',
                  get_radius=100000,
                  get_color=[255, 0, 255],   # Pink
                  pickable=True)
    layer3 = pdk.Layer('ScatterplotLayer',
                  data=df.loc[df['Elevation (m)'] < 2500],
                  get_position='[lon, lat]',
                  get_radius=100000,
                  get_color=[0, 255, 255],   # Light Blue
                  pickable=True)
    layer4 = pdk.Layer('ScatterplotLayer',
                  data=df.loc[df['Elevation (m)'] < 0],
                  get_position='[lon, lat]',
                  get_radius=100000,
                  get_color=[0, 0, 255],   # Dark Blue
                  pickable=True)
    st.sidebar.write("Colors of elevation:")
    st.sidebar.write("Elevation >5000 : Red")
    st.sidebar.write("5000< Elevation >2500 : Pink")
    st.sidebar.write("2500< Elevation >0 : Light Blue")
    st.sidebar.write("Elevation <0 : Dark Blue")
    # Create map and using layers and type of map
    tool_tip = {"html": "Volcanoes Name:<br/> <b>{Volcano Name}</b> ",
            "style": {"backgroundColor": "steelblue",
                        "color": "white"}}
    map_build = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        layers=[layer1, layer2, layer3, layer4],
        tooltip=tool_tip)
    st.pydeck_chart(map_build)


def main():
    global vol_type
    st.title("David Barre's Final Project")
    st.write("Welcome to the volcanoes data! Select a page to begin!")
    # Read in data file and change the "last known eruption" to integers
    df = pd.read_csv('volcanoes.csv', encoding='latin-1')
    vol_type = df["Primary Volcano Type"].unique().astype(list)
    df.loc[df["Last Known Eruption"] != "Unknown", "Last Known Eruption"] = df["Last Known Eruption"].str.replace(' BCE', '-').str.replace(' CE', "")
    mask = df["Last Known Eruption"].str.endswith('-')
    df.loc[mask, "Last Known Eruption"] = '-' + df.loc[mask, "Last Known Eruption"].str[: -1]
    df["Last Known Eruption"] = pd.to_numeric(df["Last Known Eruption"], errors='coerce')
    # Have three pages on streamlit with "Start Here"
    page = st.selectbox("Choose your page", ["Start Here", "Page 1: Bar Chart", "Page 2: Scatter Plot", "Page 3: Map"])
    if page == "Page 1: Bar Chart":
        page_1(df)
    elif page == "Page 2: Scatter Plot":
        page_2(df)
    elif page == "Page 3: Map":
        page_3(df)


main()
