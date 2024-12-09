import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Costa del Sol Property Viewer", layout="wide")

file_path = 'https://xlasj05.blob.core.windows.net/csv/idealista_data_clusters.csv'

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

data = load_data(file_path)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
        font-family: Arial, sans-serif;
    }
    .green-icon {
        color: green;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and Description
st.title("Costa del Sol Property Viewer")
st.markdown("Use the filters in the sidebar to narrow down your property search. "
            "You'll find properties that match your criteria below. "
            "Click on 'View' for more details about each property.")

with st.sidebar:
    st.header("Filter Properties")
    st.markdown("Use these filters to refine the list of properties. "
                "Collapse sections to simplify the view.")

    # Price and Size Filters
    with st.expander("Price and Size", expanded=True):
        price_min_k = st.number_input(
            'Minimum Property Price (k€)',
            min_value=0,
            value=int(data['price'].min() / 1000),
            help="Set the minimum price in thousands of euros."
        )
        price_max_k = st.number_input(
            'Maximum Property Price (k€)',
            min_value=0,
            value=int(data['price'].max() / 1000),
            help="Set the maximum price in thousands of euros."
        )
        price_min = price_min_k * 1000
        price_max = price_max_k * 1000

        size_min = st.number_input(
            'Minimum Size (m²)',
            min_value=0,
            value=int(data['size'].min()),
            help="Set the minimum property size in square meters."
        )
        size_max = st.number_input(
            'Maximum Size (m²)',
            min_value=0,
            value=int(data['size'].max()),
            help="Set the maximum property size in square meters."
        )

    # Distance, Rent, and ROI Filters
    with st.expander("Distance, Rent, and ROI", expanded=False):
        airport_distance_max = st.number_input(
            'Max Airport Distance (km)',
            min_value=0,
            max_value=int(data['airport_distance'].max()),
            value=int(data['airport_distance'].max()),
            help="Filter properties based on their distance to the airport."
        )

        av_rent_min, av_rent_max = st.slider(
            'Expected Daily Rent (€)',
            int(data['av_rent'].min()),
            int(data['av_rent'].max()),
            (int(data['av_rent'].min()), int(data['av_rent'].max())),
            help="Set a range for the expected daily rent."
        )

        # ROI filter
        # Assuming ROI is numeric and we can access its min/max
        roi_min = float(data['ROI'].min())
        roi_max = float(data['ROI'].max())
        selected_roi_range = st.slider(
            'ROI (%)',
            min_value=round(roi_min,1),
            max_value=round(roi_max,1),
            value=(round(roi_min,1), round(roi_max,1)),
            help="Filter properties by their Return on Investment."
        )

    # Rooms, Municipality, and Property Types
    with st.expander("Rooms, Location, and Type", expanded=False):
        rooms_selected = st.multiselect(
            'Number of Rooms',
            sorted(data['rooms'].unique()),
            default=[],
            help="Select one or more room counts to filter properties."
        )

        municipality_selected = st.multiselect(
            'Municipality',
            sorted(data['municipality'].unique()),
            default=[],
            help="Filter properties by specific municipalities."
        )

        property_types = sorted(data['propertyType'].unique())
        desired_defaults = ['flat', 'penthouse', 'studio']
        valid_defaults = [d for d in desired_defaults if d in property_types]

        property_type_selected = st.multiselect(
            'Property Type',
            property_types,
            default=valid_defaults,
            help="Select property types to include."
        )

    # Amenities
    with st.expander("Amenities", expanded=False):
        restaurants_filter = st.selectbox(
            'Near Restaurants', ['All', 'Yes', 'No'],
            help="Filter properties near restaurants."
        )
        hospitals_filter = st.selectbox(
            'Near Hospitals', ['All', 'Yes', 'No'],
            help="Filter properties near hospitals."
        )
        clinics_filter = st.selectbox(
            'Near Clinics', ['All', 'Yes', 'No'],
            help="Filter properties near clinics."
        )
        shops_filter = st.selectbox(
            'Near Shops', ['All', 'Yes', 'No'],
            help="Filter properties near shops."
        )

# Filtering data
filtered_data = data[
    (data['price'] >= price_min) &
    (data['price'] <= price_max) &
    (data['size'] >= size_min) &
    (data['size'] <= size_max) &
    (data['airport_distance'] <= airport_distance_max) &
    (data['av_rent'] >= av_rent_min) &
    (data['av_rent'] <= av_rent_max) &
    (data['ROI'] >= selected_roi_range[0]) &
    (data['ROI'] <= selected_roi_range[1])
]

if property_type_selected:
    filtered_data = filtered_data[filtered_data['propertyType'].isin(property_type_selected)]

if rooms_selected:
    filtered_data = filtered_data[filtered_data['rooms'].isin(rooms_selected)]

if municipality_selected:
    filtered_data = filtered_data[filtered_data['municipality'].isin(municipality_selected)]

if restaurants_filter != 'All':
    filtered_data = filtered_data[filtered_data['restaurants'] == (1 if restaurants_filter == 'Yes' else 0)]

if hospitals_filter != 'All':
    filtered_data = filtered_data[filtered_data['hospitals'] == (1 if hospitals_filter == 'Yes' else 0)]

if clinics_filter != 'All':
    filtered_data = filtered_data[filtered_data['clinics'] == (1 if clinics_filter == 'Yes' else 0)]

if shops_filter != 'All':
    filtered_data = filtered_data[filtered_data['shops'] == (1 if shops_filter == 'Yes' else 0)]

def format_amenity(value):
    if value == 1:
        return '<span class="green-icon">✔</span>'
    return ''

filtered_data['Restaurants'] = filtered_data['restaurants'].apply(format_amenity)
filtered_data['Shops'] = filtered_data['shops'].apply(format_amenity)

# Sort data by propertyCode in descending order
filtered_data = filtered_data.sort_values(by='propertyCode', ascending=False)

# Make URL clickable
filtered_data['Link'] = filtered_data['url'].apply(lambda x: f'<a href="{x}" target="_blank">View</a>')

columns_to_display = ['ROI', 'price', 'size', 'rooms', 'bathrooms', 'Restaurants', 'Shops', 'av_rent', 'airport_distance', 'municipality', 'Link', 'propertyCode']

filtered_data_display = filtered_data[columns_to_display].copy()

# Perform numeric formatting before rename
filtered_data_display['price'] = filtered_data_display['price'].apply(lambda x: f"{int(x):,}".replace(",", " "))
filtered_data_display['size'] = filtered_data_display['size'].astype(int)
filtered_data_display['av_rent'] = filtered_data_display['av_rent'].astype(int)
filtered_data_display['municipality'] = filtered_data_display['municipality'].astype(str)

# ROI with one decimal place and a '%' sign
filtered_data_display['ROI'] = filtered_data_display['ROI'].apply(lambda x: f"{x:.1f} %")

# airport_distance to zero decimal places
filtered_data_display['airport_distance'] = filtered_data_display['airport_distance'].round(0).astype(int)

# Rename columns
filtered_data_display = filtered_data_display.rename(columns={
    'ROI': '<span title="Estimated Return on Investment">ROI</span>',
    'price': '<span title="Total price for apartment in €">Price</span>',
    'size': '<span title="Size in m²">Size</span>',
    'rooms': '<span title="Rooms">🛏</span>',
    'bathrooms': '<span title="Bathrooms">🛁</span>',
    'Restaurants': '<span title="Restaurants">🍽</span>',
    'Shops': '<span title="Shops">🛒</span>',
    'av_rent': '<span title="Expected average daily rent in €">Rent</span>',
    # airport_distance is icon only
    'airport_distance': '<span title="Airport Distance">✈</span>',
    'municipality': '<span title="Municipality">Municipality</span>',
    'Link': '<span title="Get to original advertisement">Link</span>',
    'propertyCode': '<span title="Unique code of idealista.com">Code</span>'
})

st.subheader("Search Results")

result_count = len(filtered_data_display)
st.write(f"Found {result_count} properties matching the criteria.")

table_html = filtered_data_display.to_html(escape=False, index=False)
table_html = table_html.replace("<thead>", "<thead style='text-align:center'>")

st.write(table_html, unsafe_allow_html=True)

st.write("Use the table controls to navigate through pages of results.")
