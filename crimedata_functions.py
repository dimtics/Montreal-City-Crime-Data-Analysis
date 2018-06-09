# Several functions used in different places in the analysis are defined here.

import pandas as pd
import numpy as np
import folium
from folium import plugins
from IPython.display import display_html, HTML
from geopy.geocoders import Nominatim
import json


# Plotly packages
import plotly
from plotly import tools
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot


# define chart marker colors in two lists
markercol = ['rgba(31, 119, 180, 0.5)', 'rgba(255, 127, 14, 0.5)',
             'rgba(50, 171, 96, 0.5)', 'rgba(214, 39, 40, 0.5)',
            'rgba(148, 103, 189, 0.5)', 'rgba(140, 86, 75, 0.5)']
linecol = ['rgba(31, 119, 180, 1.0)', 'rgba(255, 127, 14, 1.0)',
            'rgba(50, 171, 96, 1.0)', 'rgba(214, 39, 40, 1.0)',
            'rgba(148, 103, 189, 1.0)', 'rgba(140, 86, 75, 1.0)']


def map_data(mappings, x):
    '''a function to map columns descriptions in French to English'''
    for i, j in mappings:
        if i == x:
            return j



def embed_map(map):
    '''a function to embed map in notebook '''
    map.save(outfile="map.html")
    return HTML('<iframe src="{i}" style="width: 100%; height: 510px; border: none"></iframe>'.format(i="map.html"))



def generate_map(df, yr):
    '''a function for creating an interactive map'''

    # exclude null location values
    ref = df[(df['YEAR'] == yr) & (df['COORDS'] != (1.0, 1.0))].copy()

    # create base map
    crimemap = folium.Map(location=[ref['LAT'].mean(), ref['LON'].mean()], zoom_start=11)

    # create an instance of marker cluster for crimes in the dataset
    crimes = plugins.MarkerCluster().add_to(crimemap)

    # loop through the dataset and add each crime point to the marker cluster
    for lat, lon, category in zip(ref['LAT'], ref['LON'], ref['ADAPTED_CATEGORY']):
        folium.Marker(location=[lat, lon], icon=None, popup=category).add_to(crimes)
        
    return embed_map(crimemap)



def extract_address(col):
    '''a function to extract addresses from latitudes and longitudes'''
    coord = list(col)
    slist = []
    geolocator = Nominatim()
    for i in coord:
        jlist = []
        location = geolocator.reverse(i, timeout=10)

        # write results as json strings
        json_string = json.dumps(location.raw)

        # convert json to dict
        dat = json.loads(json_string)

        # extract neighborhood address
        for j in dat['address'].keys():
            if j not in ['house_number', 'city', 'region', 'state', 'postcode','country', 'country_code']:
                jlist.append(dat['address'][j])
        locstr = ", ".join(jlist)
        slist.append(locstr)
    return slist



def plotchart(chdata, chlayout, titlelist, yearlist, subtitlelist):
    '''a function to plot a chart with 1 row and 3 columns figure'''

    # define subplots
    fig = tools.make_subplots(rows=1, cols=3,
        subplot_titles=(["<b>{}</b>".format(i) for i in subtitlelist]), 
        shared_yaxes=True,horizontal_spacing=(0.05),print_grid=False)

    # an empty list to hold chart data definitions for each plot
    trace_list = []    
    for i in range(3):
        data = chdata['trace_data'][chdata['trace_data']['YEAR'] == yearlist[i]]
        tracex = go.Bar(x=data[chdata['x']], y=data[chdata['y']], name=titlelist[i], width=0.7,
            text=data[chdata['y']], textposition='outside', hoverinfo='text',
            outsidetextfont=dict(size='10'), cliponaxis=False,
            marker=dict(color=markercol[:3][i], line=dict(color=linecol[:3][i], width=1)))
        trace_list.append(tracex)

        # define each subplot order of selection
        m = np.array([1, 1, 1, 2, 1, 3]).reshape(3, 2)

        # append each subplot data definitions to the figure instance
        fig.append_trace(trace_list[i], m[i][0], m[i][1])

    # define layout settings
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=12)

    for i in range(1, 4):
        fig['layout']['yaxis' + '{}'.format(i)].update(title=chlayout['yaxistitle'],
            titlefont=dict(size=12, color='rgb(107, 107, 107)'), showticklabels=False, showgrid=True)

        fig['layout']['xaxis' + '{}'.format(i)].update(titlefont=dict(size=11, color='rgb(107, 107, 107)'),
            tickfont=dict(size=11, color='rgb(107, 107, 107)'), tickangle=chlayout['tickangle'])

    # update layout settings
    fig['layout'].update(height=chlayout['height'], width=chlayout['width'], showlegend=False,
        autosize=False, title=chlayout['title'], titlefont=dict(size=14),
        paper_bgcolor='rgba(245, 246, 249, 1)', plot_bgcolor='rgba(245, 246, 249, 1)')

    return iplot(fig)
