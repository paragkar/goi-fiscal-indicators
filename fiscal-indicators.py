import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import OrderedDict, defaultdict
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import datetime as dt 
import calendar
import time
from PIL import Image
import re
import io
import msoffcrypto
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from deta import Deta
import seaborn as sns

pd.set_option('future.no_silent_downcasting', True)


#--------hide streamlit style and buttons--------------

hide_st_style = '''
				<style>
				#MainMenu {visibility : hidden;}
				footer {visibility : hidder;}
				header {visibility :hidden;}
				<style>
				'''
st.markdown(hide_st_style, unsafe_allow_html =True)

#--------Functions for loading File Starts---------------------



@st.cache_resource
def loadfile():
	password = st.secrets["db_password"]
	excel_content = io.BytesIO()
	with open("goi-fiscal-indicators.xlsx", 'rb') as f:
		excel = msoffcrypto.OfficeFile(f)
		excel.load_key(password)
		excel.decrypt(excel_content)

	#loading data from excel file
	xl = pd.ExcelFile(excel_content)
	sheet = xl.sheet_names
	df = pd.read_excel(excel_content, sheet_name=sheet)
	return df


# Main Program Starts Here

df = loadfile()["Sheet1"]



# Ensuring the Date column is of datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Sorting dataframe by Date to ensure proper animation sequence
df = df.sort_values(by='Date')

# Convert Date column to string without time
df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')

# Streamlit app
st.title("Economic Metrics Over Time")

# Sidebar for metric selection
selected_metrics = st.sidebar.multiselect("Select Metrics to Display", df['Metric'].unique(), df['Metric'].unique())

# Filter dataframe based on selected metrics
filtered_df = df[df['Metric'].isin(selected_metrics)]

# Plotly animation setup
fig = px.scatter(filtered_df, x="Value", y="Metric", animation_frame="Date_str", animation_group="Metric",
				 color="Metric", range_x=[filtered_df['Value'].min() - 1, filtered_df['Value'].max() + 1],
				 title="Economic Metrics Over Time")

# Adding the date label on top of the chart
fig.update_layout(
	xaxis_title="Value as Percentage of GDP",
	yaxis_title="Metric",
	height=600,  # Adjust the height to make the plot more visible
	title={
		'text': "Economic Metrics Over Time",
		'y': 0.9,
		'x': 0.5,
		'xanchor': 'center',
		'yanchor': 'top'
	},
	sliders=[{
		'steps': [
			{
				'args': [
					[date_str],
					{
						'frame': {'duration': 300, 'redraw': True},
						'mode': 'immediate',
						'transition': {'duration': 300}
					}
				],
				'label': date_str,
				'method': 'animate'
			}
			for date_str in df['Date_str'].unique()
		],
		'x': 0,
		'xanchor': 'left',
		'y': 0,  # Adjust this value to move the slider closer to the chart
		'yanchor': 'top'
	}]
)

# Adding an initial annotation for the date
initial_date_annotation = {
	'x': 0.5,
	'y': 1.1,
	'xref': 'paper',
	'yref': 'paper',
	'text': f'Date: {filtered_df["Date_str"].iloc[0]}',
	'showarrow': False,
	'font': {
		'size': 16
	}
}

fig.update_layout(annotations=[initial_date_annotation])

# Display the Plotly figure
st.plotly_chart(fig)

