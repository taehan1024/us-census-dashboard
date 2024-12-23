############################################################################
# import libraries
import requests
import pandas as pd


############################################################################
# get_census_data function given year, variable
def get_census_data(year_num, var, var_name):
    api_url = f"https://api.census.gov/data/{year_num}/acs/acs5?get=NAME,{var}&for=state:*"
    response = requests.get(api_url)
    response_json = response.json()

    data = response_json[1:]

    state = [str(row[0]) for row in data]
    var = [int(row[1]) for row in data]
    state_id = [int(row[2]) for row in data]

    df = pd.DataFrame({
    'State': state, 
    'state_id': state_id,
    'year': year_num,    
    var_name: var})
    
    df = df[['State', 'state_id', 'year', var_name]] 
    
    return(df)



############################################################################
# total_population for 2012 ~ 2022, except District of Columbia and Puerto Rico
year_list = range(2012, 2023)
census_data = pd.DataFrame()

for yr in year_list:
    year_data = get_census_data(yr, 'B01001_001E', 'total_population')
    census_data = pd.concat([census_data, year_data], ignore_index=True)

census_data = census_data[~census_data['State'].isin(['District of Columbia', 'Puerto Rico'])]




############################################################################
# add abbreviation state codes
state_abbr_codes = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

census_data['state_code'] = census_data['State'].map(state_abbr_codes)



############################################################################
# add land areas in sq.mi. and population densities
state_land_areas = {
    'Alabama': 50645,
    'Alaska': 570641,
    'Arizona': 113594,
    'Arkansas': 52035,
    'California': 155779,
    'Colorado': 103642,
    'Connecticut': 4842,
    'Delaware': 1949,
    'District of Columbia': 61,
    'Florida': 53625,
    'Georgia': 57513,
    'Hawaii': 6423,
    'Idaho': 82643,
    'Illinois': 55519,
    'Indiana': 35826,
    'Iowa': 55857,
    'Kansas': 81759,
    'Kentucky': 39486,
    'Louisiana': 43204,
    'Maine': 30843,
    'Maryland': 9707,
    'Massachusetts': 7800,
    'Michigan': 56539,
    'Minnesota': 79627,
    'Mississippi': 46923,
    'Missouri': 68742,
    'Montana': 145546,
    'Nebraska': 76824,
    'Nevada': 109781,
    'New Hampshire': 8953,
    'New Jersey': 7354,
    'New Mexico': 121298,
    'New York': 47126,
    'North Carolina': 48618,
    'North Dakota': 69001,
    'Ohio': 40861,
    'Oklahoma': 68595,
    'Oregon': 95988,
    'Pennsylvania': 44743,
    'Rhode Island': 1034,
    'South Carolina': 30061,
    'South Dakota': 75811,
    'Tennessee': 41235,
    'Texas': 261232,
    'Utah': 82170,
    'Vermont': 9217,
    'Virginia': 39490,
    'Washington': 66456,
    'West Virginia': 24038,
    'Wisconsin': 54158,
    'Wyoming': 97093
}


census_data['land_area'] = census_data['State'].map(state_land_areas)
census_data['population_density'] = census_data['total_population']/census_data['land_area']



############################################################################
# add change from populations in 2012
census_data_2012 = census_data[census_data['year'] == 2012]
census_data = pd.merge(census_data, census_data_2012[['State', 'total_population']].rename(columns={'State': 'State', 'total_population': 'total_population_2012'}), on='State', how='left')
census_data['population_change'] = census_data['total_population'] - census_data['total_population_2012']
census_data = census_data[census_data['year']!=2012]

############################################################################
# write a csv file
census_data = census_data[['State', 'state_code', 'state_id', 'year', 'total_population', 'land_area', 'population_density', 'population_change']].sort_values(by = ['year', 'State'], ascending=[False, True])

census_data.to_csv('census_data.csv', index=False)




