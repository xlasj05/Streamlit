import streamlit as st
import pandas as pd

# Set Streamlit page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Costa del Sol Property Viewer", layout="wide")

# Azure Blob Storage URL
file_path = 'https://xlasj05.blob.core.windows.net/csv/idealista_A10.csv'

# Load data from Azure Blob Storage
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

data = load_data(file_path)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
        color: black;
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

# Title
st.title('Costa del Sol Property Viewer')

# Sidebar for filters
with st.sidebar:
    st.header("Filter Properties")

    # Property price range as input fields in thousands of euros (k€)
    price_min_k = st.number_input('Minimum Property Price (k€)', min_value=0, value=int(data['price'].min() / 1000))
    price_max_k = st.number_input('Maximum Property Price (k€)', min_value=0, value=int(data['price'].max() / 1000))

    # Convert the selected price range back to full euros
    price_min = price_min_k * 1000
    price_max = price_max_k * 1000

    # Size range as input fields
    size_min = st.number_input('Minimum Size (m²)', min_value=0, value=int(data['size'].min()))
    size_max = st.number_input('Maximum Size (m²)', min_value=0, value=int(data['size'].max()))

    # Airport distance slider
    airport_distance_max = st.number_input(
        'Airport Distance (km)',
        min_value=0,
        max_value=int(data['airport_distance'].max()),
        value=int(data['airport_distance'].max())
    )

    # Expected daily rent slider
    av_rent_min, av_rent_max = st.slider(
        'Expected Daily Rent (€)',
        int(data['av_rent'].min()),
        int(data['av_rent'].max()),
        (int(data['av_rent'].min()), int(data['av_rent'].max()))
    )

    # Number of rooms and municipality filters
    rooms_selected = st.multiselect(
        'Number of Rooms',
        sorted(data['rooms'].unique()),
        default=[]
    )

    municipality_selected = st.multiselect(
        'Municipality',
        sorted(data['municipality'].unique()),
        default=[]
    )

    # Filters for nearby amenities
    restaurants_filter = st.selectbox('Near Restaurants', ['All', 'Yes', 'No'])
    hospitals_filter = st.selectbox('Near Hospitals', ['All', 'Yes', 'No'])
    clinics_filter = st.selectbox('Near Clinics', ['All', 'Yes', 'No'])
    shops_filter = st.selectbox('Near Shops', ['All', 'Yes', 'No'])

    # Property type filter
    property_types = sorted(data['propertyType'].unique())
    property_type_selected = st.multiselect(
        'Property Type',
        property_types,
        default=['flat', 'penthouse', 'studio']
    )

# Filtering data based on user input
filtered_data = data[
    (data['price'] >= price_min) &
    (data['price'] <= price_max) &
    (data['size'] >= size_min) &
    (data['size'] <= size_max) &
    (data['airport_distance'] <= airport_distance_max) &
    (data['av_rent'] >= av_rent_min) &
    (data['av_rent'] <= av_rent_max)
]

# Apply filters if values are selected
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

# Custom formatting for Restaurants and Shops with icons
def format_amenity(value):
    if value == 1:
        return '<span class="green-icon">✔</span>'  # Green check icon
    return ''  # Empty if 0

filtered_data['Restaurants'] = filtered_data['restaurants'].apply(format_amenity)
filtered_data['Shops'] = filtered_data['shops'].apply(format_amenity)

# Sort data by Code in descending order
filtered_data = filtered_data.sort_values(by='propertyCode', ascending=False)

# Make URL clickable and rename to 'Link'
filtered_data['Link'] = filtered_data['url'].apply(lambda x: f'<a href="{x}" target="_blank">View</a>')

# Select and format columns for display, with ROI as the first column
columns_to_display = ['ROI', 'price', 'size', 'rooms', 'bathrooms', 'Restaurants', 'Shops', 'av_rent', 'airport_distance', 'municipality', 'Link', 'propertyCode']
filtered_data_display = filtered_data[columns_to_display].rename(columns={
    'ROI': 'ROI',
    'propertyCode': 'Code',
    'price': 'Price',
    'size': 'Size',
    'rooms': 'Rooms',
    'bathrooms': 'Bathrooms',
    'av_rent': 'Rent',
    'airport_distance': 'Airport km',
    'municipality': 'Municipality'
})

# Adjust ROI to percentage format by multiplying by 100
filtered_data_display['ROI'] = filtered_data_display['ROI'] * 100
filtered_data_display['ROI'] = filtered_data_display['ROI'].apply(lambda x: f"{x:.1f} %")

# Format other columns for display
filtered_data_display['Price'] = filtered_data_display['Price'].apply(lambda x: f"{int(x):,}".replace(",", " "))
filtered_data_display['Size'] = filtered_data_display['Size'].astype(int)
filtered_data_display['Rent'] = filtered_data_display['Rent'].astype(int)
filtered_data_display['Airport km'] = filtered_data_display['Airport km'].round(0).astype(int)

st.subheader("Search Results")
st.write(f"Found {len(filtered_data_display)} properties matching the criteria")

# Display the formatted table with custom icons and clickable Link
st.write(filtered_data_display.to_html(escape=False, index=False), unsafe_allow_html=True)

# Paging to manage data load
st.write("Use the table controls to navigate through pages of results.")
