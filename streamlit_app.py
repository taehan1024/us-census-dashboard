#%%
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear
import requests

#%%
#######################
# Page configuration
st.set_page_config(
    page_title = "U.S. Census Dashboard",
    page_icon = "✅",
    layout = "wide",
    initial_sidebar_state = "expanded")


#%%
#######################
# load data

@st.cache_data(ttl=1800, show_spinner="Loading the dashboard...")
def load_geojson(url):
    geojson = requests.get(url).json()
    
    return geojson


@st.cache_data(ttl=1800, show_spinner="Loading the dashboard...")
def load_data(url):
    df = pd.read_csv(url)
    
    return df


state_geo = load_geojson('https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json')
census_data = load_data("data/census_data.csv")



#%%
# Sidebar

with st.sidebar:
    st.title('U.S. Population')
       
    # select variable
    variable_type = st.radio("Select dashboard", ["Total Population", "Population Density", "Population Change (from 2012)"], index=0)
    
    if variable_type == "Total Population":
        census_data['variable_interested'] = census_data['total_population']
                
    elif variable_type == "Population Density":
        census_data['variable_interested'] = census_data['population_density']
    
    else:
        census_data['variable_interested'] = census_data['population_change']
    
    # select year
    year_list = list(census_data['year'].unique())
    year_list.sort(reverse = True)
    year_selected = st.selectbox('Select year', year_list)
    
    @st.cache_data(ttl=1800, show_spinner="Loading the dashboard...")
    def filter_by_year(df, yr):
        df_filter = census_data[census_data['year'] == yr].sort_values(by="variable_interested", ascending=False)
        df_filter['rank'] = df_filter['variable_interested'].rank(method='first', ascending=False).astype(int)       
        
        return df_filter
       
    df_selected = filter_by_year(census_data, year_selected)
    
     
    # ranking type
    ranking_type = st.radio("Select ranking", ["All States", "Top 5 & Bot 5"], index=1)
    
    
    # color type
    color_type = st.radio("Select color coding", ["Individually", "By group"], index=1)
    
    

#%%
# Titles

app_title = f"US census map dashboard {year_selected}"
app_subtitle = 'Source: US census gov.'


#%%


def display_metrics():
    metric_col1, metric_col2, metric_col3 = st.columns([0.2, 0.4, 0.4]) 
    
    rank_metric = 1
    state_metric = df_selected[df_selected['rank'] == 1]['State'].values[0]
    variable_interested_metric = int(df_selected[df_selected['rank'] == 1]['variable_interested'].values[0])

    if st_map['last_active_drawing']:
        state_code_clicked = st_map['last_active_drawing']['id']
        rank_metric = rank_dict[state_code_clicked]
        state_metric = st_map['last_active_drawing']['properties']['name']
        variable_interested_metric = int(st_map['last_active_drawing']['properties']['variable_interested'])

    metric_col1.metric(label=':grey-background[Rank]', value=rank_metric)
    metric_col2.metric(label=':grey-background[State]', value=state_metric)
    metric_col3.metric(label=f':grey-background[{variable_type_cleaned}]', value=f"{variable_interested_metric:,}")
    



#%%
# Columns

col = st.columns([0.7, 0.3], gap='small')


with col[0]:
        
    variable_type_cleaned = variable_type.replace(" from 2012", "")
    
    st.markdown(f'#### {variable_type_cleaned} - {year_selected}')
    
    colormap = linear.YlOrRd_09.scale(
        census_data.variable_interested.min(),
        census_data.variable_interested.max())
    
    
    colormap_rank = linear.YlOrRd_09.scale(
        1,
        50)

    variable_interested_dict = df_selected.set_index('state_code')['variable_interested']
    rank_dict = df_selected.set_index('state_code')['rank']

    m = folium.Map([38, -96.5], zoom_start=4, scrollWheelZoom=False)



    if color_type == "Individually":
                        
        for feature in state_geo['features']:
            feature['properties']['variable_interested'] = str("%d" % variable_interested_dict[feature['id']])
        
        tooltip = folium.GeoJsonTooltip(
            fields=["name", "variable_interested"],
            aliases=["State:", f"{variable_type_cleaned}:"],
            localize=True,
            sticky=False,
            labels=True)    
                
        def style_function(feature):
            return {
                'fillColor': colormap(variable_interested_dict[feature['id']]),
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.6,
                }
                     
        folium.GeoJson(
            state_geo,
            name='variable_interested',
            tooltip=tooltip,
            style_function=style_function
        ).add_to(m)    
  
        folium.LayerControl().add_to(m)    
        
        st_map = st_folium(m, width=700, height=450)

        
    else:
        
        for feature in state_geo['features']:
            feature['properties']['variable_interested'] = str("%d" % variable_interested_dict[feature['id']])
        
        tooltip = folium.GeoJsonTooltip(
            fields=["name", "variable_interested"],
            aliases=["State:", f"{variable_type_cleaned}:"],
            localize=True,
            sticky=False,
            labels=True) 
        
                        
        def style_function(feature):
            rank_given = rank_dict[feature['id']]
            
            if rank_given < 18:
                fill_color = colormap_rank(50)
            elif rank_given < 34:
                fill_color = colormap_rank(25)
            else:
                fill_color = colormap_rank(1)
            
            return {
                'fillColor': fill_color,
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.6,
                }
                     
        folium.GeoJson(
            state_geo,
            name='variable_interested',
            tooltip=tooltip,
            style_function=style_function
        ).add_to(m)    
  
        folium.LayerControl().add_to(m)    
        
        st_map = st_folium(m, width=700, height=450) 
        
            
    display_metrics()


with col[1]:
    
    if ranking_type == "All States":
        variable_type_cleaned = variable_type.replace(" (from 2012)", "")
        
        st.markdown('##### All States')
        
        st.dataframe(df_selected,
                     column_order=("rank", "State", "variable_interested"),
                     hide_index=True,
                     width=None,
                     column_config={
                         "rank": st.column_config.NumberColumn(
                             "Rank",
                             min_value=1,
                             max_value=50,
                         ),                              
                        "State": st.column_config.TextColumn(
                            "States",
                        ),
                        "variable_interested": st.column_config.ProgressColumn(
                            f"{variable_type_cleaned}",
                            format="%d",
                            min_value=0,
                            max_value=max(df_selected.variable_interested),
                         )}
                     )    
    
    else:
        variable_type_cleaned = variable_type.replace(" from 2012", "")
        
        st.markdown('##### Top 5 States')
        
        st.dataframe(df_selected.head(5),
                     column_order=("rank", "State", "variable_interested"),
                     hide_index=True,
                     width=None,
                     column_config={
                         "rank": st.column_config.NumberColumn(
                             "Rank",
                             min_value=1,
                             max_value=50,
                         ),
                        "State": st.column_config.TextColumn(
                            "States",
                        ),
                        "variable_interested": st.column_config.ProgressColumn(
                            f"{variable_type_cleaned}",
                            format="%d",
                            min_value=0,
                            max_value=max(df_selected.variable_interested),
                         )}
                     )

        st.markdown('##### Bottom 5 States')

        st.dataframe(df_selected.tail(5).sort_values(by="variable_interested", ascending=False),
                     column_order=("rank", "State", "variable_interested"),
                     hide_index=True,
                     width=None,
                     column_config={
                         "rank": st.column_config.NumberColumn(
                             "Rank",
                             min_value=1,
                             max_value=50,
                         ),
                        "State": st.column_config.TextColumn(
                            "States",
                        ),
                        "variable_interested": st.column_config.ProgressColumn(
                            f"{variable_type_cleaned}",
                            format="%d",
                            min_value=0,
                            max_value=max(df_selected.variable_interested),
                         )}
                     )
        
        

    







