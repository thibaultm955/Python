import pandas as pd
import csv
import json
import urllib.request, urllib.parse, urllib.error
import plotly.express as px
import plotly.graph_objects as go




postal_code = pd.read_csv("C:/Users/thiba/OneDrive/Documents/Hays/liste-des-codes-postaux-belges-fr.csv", sep = ';')
Customer_data = pd.read_csv("C:/Users/thiba/OneDrive/Documents/Hays/CustomerData.csv")
hays_postal_code = pd.read_csv("C:/Users/thiba/OneDrive/Documents/Hays/PostalCodeData.csv")



postal_code = postal_code.rename(columns={"Code postal" : "zip"})


Customer_data_2 = Customer_data.set_index('zip') 
postal_code_2 = postal_code.set_index('zip')

joined_df = pd.merge(Customer_data_2,postal_code_2, how = 'left', on = ['zip'])

#print(joined_df)

grouped = postal_code.groupby('zip')
grouped_2 = grouped.first()


joined_df_2 = pd.merge(Customer_data_2,grouped_2, how = 'left', on = ['zip'])
#joined_df_2.to_csv(r'C:/Users/thiba/OneDrive/Documents/Hays/test.csv')

joined_df_3 = pd.merge(joined_df_2, hays_postal_code, how = 'left', on = ['zip', 'Type'])


#here we start to set up the API for Google Map
head_data = joined_df_3.head(n=1000)

url = "https://maps.googleapis.com/maps/api/geocode/json?&address="
key = "&key=AIzaSyACJ0iS9nsly5XRw4MQPuXDt-Bdzel1vYA"

i = 0
thislist  = []
thislist_2 = []

while i < len(head_data):
    final_url = url + str(head_data["zip"][i]) + "%20" + str(head_data["Localité"][i]) + key
    uh = urllib.request.urlopen(final_url)
    data = uh.read()
    info = json.loads(data)
    for s in info["results"]:
        lat = s['geometry']['bounds']['northeast']['lat']
        lng = s['geometry']['bounds']['northeast']['lng']
        thislist.append(lat)
        thislist_2.append(lng)
    i = i + 1



#create new df 
df1 = pd.DataFrame({'lat':thislist})
df2 = pd.DataFrame({'lng':thislist_2})

#we will cbind to have the dataset enriched with latitude and longitude
result = pd.concat([head_data, df1, df2], axis = 1)


#result.to_csv(r'C:/Users/thiba/OneDrive/Documents/Hays/test.csv')

#Here you have the amount spend per zip, per year and per type
grouped_by = result.groupby(['zip', 'YEAR', 'Type', 'lat', 'lng'])
grouped_by_sum = grouped_by.sum()




grouped_by_sum["Montant_By_Person"] = grouped_by_sum["Montant achat"] / grouped_by_sum["HH"]
print(grouped_by_sum)
#Here we move from the multi index to column
grouped_by_sum.reset_index(inplace=True)


fig = px.line(grouped_by_sum, x='Type', y='Montant achat', color = 'YEAR')
#fig.show()

#Group by zip code
grouped_by_zip = result.groupby(['zip', 'Localité', 'lat', 'lng'])
grouped_by_zip_sum = grouped_by_zip.sum()
grouped_by_zip_sum.reset_index(inplace=True)
#grouped_by_zip_sum['text'] = grouped_by_zip_sum['Localité'] + '<br>Montant Achat' + str(grouped_by_zip_sum['Montant achat'])

grouped_by_zip_by_year = result.groupby(['zip', 'YEAR', 'lat', 'lng'])
grouped_by_zip_year_sum = grouped_by_zip_by_year.sum()
grouped_by_zip_year_sum.reset_index(inplace=True)

print(grouped_by_zip_sum)

grouped_by_zip_sum.loc[grouped_by_zip_sum['Montant achat'] > 500000 , 'Color'] = 'Orange'
grouped_by_zip_sum.loc[grouped_by_zip_sum['Montant achat'] > 1200000, 'Color'] = 'Red' 
grouped_by_zip_sum.loc[grouped_by_zip_sum['Montant achat'] <= 500000, 'Color'] = 'Green' 


scale = 9750
fig = go.Figure()

fig.add_trace(go.Scattergeo(
    locationmode = 'country names',
    lon = grouped_by_zip_sum['lng'],
    lat = grouped_by_zip_sum['lat'],
    text = grouped_by_zip_sum['Localité'],
    marker = dict(
        size = grouped_by_zip_sum['Montant achat'] / scale,
        color = grouped_by_zip_sum['Color']
        )))

fig.update_layout(
        title_text = 'Hays case',
        showlegend = True,
        geo = go.layout.Geo(
            resolution = 50,
            scope = 'europe',
            showframe = False,
            showcoastlines = True,
            landcolor = "rgb(229, 229, 229)",
            countrycolor = "white" ,
            coastlinecolor = "white",
            projection_type = 'mercator',
            lonaxis_range= [ 2, 6.5 ],
            lataxis_range= [ 49, 51.75 ],
            domain = dict(x = [ 0, 1 ], y = [ 0, 1 ])
    )
    )

fig.show()








