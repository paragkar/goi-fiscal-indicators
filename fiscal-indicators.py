import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import io
import msoffcrypto

pd.set_option('display.max_columns', None)

# Hide Streamlit style and buttons
hide_st_style = '''
	<style>
	#MainMenu {visibility: hidden;}
	footer {visibility: hidden;}
	header {visibility: hidden;}
	</style>
	'''
st.markdown(hide_st_style, unsafe_allow_html=True)

# Load file function
@st.cache_resource
def loadfile():
	password = st.secrets["db_password"]
	excel_content = io.BytesIO()
	with open("goi-fiscal-indicators.xlsx", 'rb') as f:
		excel = msoffcrypto.OfficeFile(f)
		excel.load_key(password)
		excel.decrypt(excel_content)

	# Loading data from excel file
	df = pd.read_excel(excel_content, sheet_name="Sheet1")
	return df

# Main Program Starts Here
df = loadfile()

# Ensuring the Date column is of datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Sorting dataframe by Date to ensure proper animation sequence
df = df.sort_values(by='Date')

# Convert Date column to string without time
df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')

# Format the Value column to two decimal places and keep it as a float
df['Value'] = df['Value'].astype(float).round(2)

# Create a column to hold the value information
df['Text'] = df.apply(lambda row: f"<b>{row['Value']:.2f}</b>", axis=1)

# Streamlit app
st.title("Economic Metrics Over Time")

# Sidebar for metric selection
selected_metrics = st.sidebar.multiselect("Select Metrics to Display", df['Metric'].unique(), df['Metric'].unique())

# Filter dataframe based on selected metrics
filtered_df = df[df['Metric'].isin(selected_metrics)]

# Plotly animation setup
fig = px.scatter(filtered_df, x="Value", y="Metric", animation_frame="Date_str", animation_group="Metric",
				 color="Metric", range_x=[-filtered_df['Value'].abs().max() - 1, filtered_df['Value'].max() + 1],
				 title="", size_max=20, text="Text")

# Customize text position to the right of the dots
fig.update_traces(textposition='middle right')

# Remove y-axis labels and variable labels
fig.update_yaxes(showticklabels=True)
fig.update_traces(marker=dict(size=14))

# Draw a black line on the y-axis
fig.add_shape(type='line', x0=0, x1=0, y0=0, y1=1, line=dict(color='black', width=1), xref='x', yref='paper')

# Remove legend on the right side
fig.update_layout(showlegend=False)

# Adjust the layout
fig.update_layout(
	xaxis_title="Value as Percentage of GDP",
	yaxis_title="",
	height=800,  # Adjust the height to make the plot more visible
	margin=dict(l=10, r=40, t=100, b=40),  # Add margins to make the plot more readable
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
		'x': 0.1,
		'xanchor': 'left',
		'y': -0.2,
		'yanchor': 'top'
	}]
)

# Add initial annotation for the date
initial_date_annotation = {
	'x': 0.5,
	'y': 1.15,  # Move the date annotation closer to the top of the chart
	'xref': 'paper',
	'yref': 'paper',
	'text': f'Date: {filtered_df["Date_str"].iloc[0]}',
	'showarrow': False,
	'font': {
		'size': 16
	}
}
fig.update_layout(annotations=[initial_date_annotation])

# Custom callback to update the date annotation dynamically
def update_annotations(date_str):
	return [go.layout.Annotation(
		x=0.5,
		y=1.15,
		xref='paper',
		yref='paper',
		text=f'Date: {date_str}',
		showarrow=False,
		font=dict(size=16)
	)]

# Update annotation with each frame
for frame in fig.frames:
	date_str = frame.name
	frame['layout'].update(annotations=update_annotations(date_str))

# Custom callback to update the date annotation dynamically
fig.update_layout(
	updatemenus=[{
		'type': 'buttons',
		'showactive': False,
		'buttons': [
			{
				'label': 'Play',
				'method': 'animate',
				'args': [None, {
					'frame': {'duration': 500, 'redraw': True},
					'fromcurrent': True,
					'transition': {'duration': 300, 'easing': 'linear'}
				}]
			},
			{
				'label': 'Pause',
				'method': 'animate',
				'args': [[None], {
					'frame': {'duration': 0, 'redraw': False},
					'mode': 'immediate',
					'transition': {'duration': 0}
				}]
			}
		]
	}]
)

# Use Streamlit's container to fit the chart properly
with st.container():
    st.plotly_chart(fig, use_container_width=True)