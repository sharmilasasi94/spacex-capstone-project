# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique()

# Create the app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in launch_sites
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Success Pie Chart
    html.Div(
        dcc.Graph(id='success-pie-chart')
    ),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),

    # TASK 4: Payload vs. Launch Success Scatter Chart
    html.Div(
        dcc.Graph(id='success-payload-scatter-chart')
    )
])


# TASK 2: Callback to render the success pie chart
@app.callback(
    Output(
        component_id='success-pie-chart',
        component_property='figure'
    ),
    Input(
        component_id='site-dropdown',
        component_property='value'
    )
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        # Count successful launches at each site
        success_df = spacex_df[
            spacex_df['class'] == 1
        ]

        fig = px.pie(
            success_df,
            names='Launch Site',
            title='Total Successful Launches for All Sites'
        )

    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        # Count successful and failed launches
        outcome_counts = (
            filtered_df['class']
            .value_counts()
            .reindex([1, 0], fill_value=0)
            .rename(index={
                1: 'Success',
                0: 'Failure'
            })
            .rename_axis('Launch Outcome')
            .reset_index(name='Launch Count')
        )

        fig = px.pie(
            outcome_counts,
            values='Launch Count',
            names='Launch Outcome',
            title=f'Success vs. Failure for {entered_site}'
        )

    return fig


# TASK 4: Callback to render the payload scatter chart
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(
            component_id='site-dropdown',
            component_property='value'
        ),
        Input(
            component_id='payload-slider',
            component_property='value'
        )
    ]
)
def get_scatter_chart(entered_site, payload_range):

    # Filter by payload range
    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Filter by launch site if a specific site is selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload Mass vs. Launch Outcome',
        labels={
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'class': 'Launch Outcome',
            'Booster Version Category': 'Booster Version'
        },
        hover_data=['Launch Site']
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
