'''
Name: Sama Abu Zahra
CS 230: Section 5
Data: Cannabis Registry
URL: 

Description:

This program looks at data from the Cannabis Registry CSV, and then based on that information extracts information about locations of registries around Boston and other components such as their license status, category, etc.
'''
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
from PIL import Image
import seaborn as sns # New package installed

# Load the Cannabis Registry data
@st.cache_data
def load_data():
    data = pd.read_csv('/Users/samaabuzahra/Desktop/CS230/Project/Cannabis_Registry.csv')
    return data
data = load_data()

# This feature is used to clean the data from any NaN
data = data.dropna()
print(data)

# Page functions
# Creating the home page, which includes a welcome message and an image with a caption
def home_page():
    st.header("Welcome to the Cannabis Registry Dashboard!")
    st.write("Navigate through the application using the sidebar to explore different data insights.")
    image = Image.open('/Users/samaabuzahra/Desktop/CS230/Project/cannabis_image.jpeg')
    st.image(image, caption='Here, you will know where to go for cannabis!', use_column_width=True)

# This is somewhat of a summary about the data provided
def page_data_overview(data):
    st.header("Cannabis Registry Data Overview")
    st.write(data) # All the data is provided here.

    # The same data provided can now be filtered based on License status, which will be what the data that is shown depends on.
    st.subheader("Filter by License Status")
    selected_status = st.selectbox("Choose a License Status", options=np.insert(data['app_license_status'].unique(), 0, 'All'))
    if selected_status != 'All':
        filtered_data = data[data['app_license_status'] == selected_status]
    else:
        filtered_data = data
    st.write(filtered_data)

    # Another filter is used here where the data presented is pased on the user selecting a range of the zip code, which will then show only the people within that zip code.
    st.subheader("Filter by ZIP Code Range")
    zip_min, zip_max = int(data['facility_zip_code'].min()), int(data['facility_zip_code'].max())
    selected_zip_range = st.slider("Select a ZIP code range", zip_min, zip_max, (zip_min, zip_max))

    # Filter the data based on the ZIP code range
    filtered_data_zip = data[(data['facility_zip_code'] >= selected_zip_range[0]) & (data['facility_zip_code'] <= selected_zip_range[1])]
    st.write(filtered_data_zip)

    # For license category
    st.sidebar.subheader("Filter by License Category")
    unique_categories = data['app_license_category'].unique().tolist()
    selected_categories = st.sidebar.multiselect('Select License Categories', unique_categories,
                                                 default=unique_categories)

    # Applying the license category filter to the data
    filtered_data = data[data['app_license_category'].isin(selected_categories)]

    if not filtered_data.empty:
        # Creating a bar chart based on the categories selected; default is all the categories together.
        st.subheader("Bar Chart of License Categories")
        category_counts = filtered_data['app_license_category'].value_counts()
        fig, ax = plt.subplots()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                  '#17becf'] # These are the hexadecimal color codes.
        category_counts.plot(kind='bar', ax=ax,color=colors[:len(category_counts)])
        ax.set_title("Number of Entries per License Category")
        ax.set_xlabel("License Category")
        ax.set_ylabel("Count")
        st.pyplot(fig)
    else:
        st.write("No data available for selected categories.")

# Interactive map visualization is created here
# This function starts with the current values for latitude, longitude, zoom, and pitch
def create_scatterplot_layer(data, latitude, longitude, zoom, pitch):
    return pdk.Layer(
        'ScatterplotLayer',
        data=data,
        get_position='[longitude, latitude]',
        get_color='[155, 10, 0, 150]',
        get_radius=100,
    )
def page_visualizations(data):
    st.header("Data Visualizations")
    st.subheader("Location Scatter Plot")
    st.write("This scatter plot shows the geographical distribution of cannabis registries in Boston. You can change the latitude, longitude, zoom, and pitch through the widgets presented in the sidebar to be able to explore the different areas, based on your pleasing.")
    lat = st.sidebar.number_input('Latitude', value=42.3601, format="%.4f")
    lon = st.sidebar.number_input('Longitude', value=-71.0589, format="%.4f")
    zoom = st.sidebar.slider('Zoom Level', 0, 20, 11)
    pitch = st.sidebar.slider('Pitch', 0, 60, 50)

    # Here the pydeck chart appears in Streamlit and interacts with user based on the specific data entered for the latitude, longitude, zoom, and pitch
    scatterplot_layer = create_scatterplot_layer(data, lat, lon, zoom, pitch)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=zoom,
            pitch=pitch,
        ),
        layers=[scatterplot_layer],
    ))

    # Histogram is created that shows the number of licenses per each zip code
    st.subheader("Histogram of Licenses by ZIP Code")
    st.write("This Histogram presents the number of licenses that are distributed within the various zip codes.")
    fig, ax = plt.subplots()
    data['facility_zip_code'].value_counts().plot(kind='bar') # Facility zip code is taken from the data
    plt.xlabel('ZIP Code')
    plt.ylabel('Number of Licenses')
    st.pyplot(fig)

    st.subheader("License Status by Zip Code")
    st.write("The table below breaks down the number of licenses by their status for each ZIP code. You can make the table to be fullscreen to see the results more clearly, or download the results as a CSV, or even search any result you may want to focus on.")
    pivot_table = pd.pivot_table(data, values='id_name_first', index='facility_zip_code', columns='app_license_status', aggfunc='count')
    st.write(pivot_table)

def page_analysis(data):
    st.header("Data Analysis")

    # Bar Chart for License Status
    st.subheader("License Status Distribution")
    status_count = data['app_license_status'].value_counts()
    fig, ax = plt.subplots()
    colors = ['pink', 'lightblue', 'purple', 'yellow', 'orange']
    ax.bar(status_count.index, status_count.values, color=colors[:len(status_count)])
    ax.set_xlabel('License Status')
    ax.set_ylabel('Count')
    ax.set_title('License Status Distribution')
    st.pyplot(fig)

    # Pie Chart
    st.subheader("License Category Distribution")
    license_category_count = data['app_license_category'].value_counts()
    explode_values = [0.1 if value < license_category_count.max() * 0.1 else 0 for value in license_category_count] # This list comprehension is used to 'explode' values in the pie chart. This feature is the reason the pie chart seems to be sliced, if the count is less than 10%.
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.pie(license_category_count, explode=explode_values, labels=None, autopct='%1.1f%%', startangle=90,
            colors=plt.cm.tab20.colors)
    plt.legend(license_category_count.index, title="Categories", bbox_to_anchor=(1, 0, 0.5, 1))
    ax1.axis('equal')
    st.pyplot(fig1)

    # This part is a vital piece of code, as I extracted this from a package called Seaborn. I chose to do a heatmap based on the information provided. In this case, my heatmap shows the distribution of different license categories accross various zip codes.
    st.subheader("Heatmap of License Categories by ZIP Code")
    st.write("The Heatmap below represents the concentration of various cannabis license categories across different ZIP codes. More intense colors show a higher concentration of licenses!")
    pivot_table = pd.pivot_table(data, values='id_name_first', index='facility_zip_code',
                                 columns='app_license_category', aggfunc='count', fill_value=0)
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, annot=True, fmt="d", cmap="YlGnBu") # This is the creation of the heatmap with Seaborn
    plt.title('Heatmap of License Categories by ZIP Code')
    plt.ylabel('ZIP Code')
    plt.xlabel('License Category')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def citations(data):
    st.header("Citations")
    st.write("Data and images sourced from various websites.")
    st.write("1. [Marijuana Stock Photos](https://www.istockphoto.com/photos/marijuana)")
    st.write("2. [Seaborn Charts](https://seaborn.pydata.org/examples/many_pairwise_correlations.html)")
    st.balloons()

# Main app
def main():
    data = load_data()

    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio("Choose a page:", ["Home", "Data Overview", "Visualizations", "Analysis","Citations"])

    # Page display and what to show if whatever page is selected through the defined functions.
    if page_selection == "Home":
        home_page()
    elif page_selection == "Data Overview":
        page_data_overview(data)
    elif page_selection == "Visualizations":
        page_visualizations(data)
    elif page_selection == "Analysis":
        page_analysis(data)
    elif page_selection == "Citations":
        citations(data)

if __name__ == "__main__":
    main()
