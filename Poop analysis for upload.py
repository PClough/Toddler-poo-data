# -*- coding: utf-8 -*-
"""
Poop analysis

Created 2020

@author: PClough
"""

import pandas as pd
import numpy as np
import chart_studio
import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots
from scipy import stats
import datetime as dt
from time import strptime
import calendar
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import vlc

df = pd.read_excel("Poo Data.xlsx", engine='openpyxl')

chart_studio.tools.set_credentials_file(username='YOUR USERNAME HERE', api_key='YOUR API HERE')

#%% Histogram of size of poos

# Replace sizes of 1, 2, and 3 in "size of poo?" heading to be small, medium and large
df['Size of poo? '].replace([1, 2, 3], ['Small', 'Medium', 'Poonarmi'], inplace = True)

fig = go.Figure()
fig.add_trace(go.Histogram(x = df['Size of poo? '],
                name = 'Poop',
                xbins = dict(
                        start = "Small",
                        ),
                marker_color = ('rgb(166,86,50)')))

fig.update_layout(
        title_text = "Size of the poo poo's",
        yaxis_title = "Count",
        font = dict(size = 16))

plot(fig)

#%% Violin plot for day of week on x axis and type of poo on y axis

fig2 = go.Figure()

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Date_column = df['When did the poo occur? '].dt.strftime("%a")

for day in days:
    fig2.add_trace(go.Violin(x = Date_column[Date_column == day],
        y = df['Type of poop 💩? '][Date_column == day],
        name = day,
        box_visible = True,
        meanline_visible = True,
        showlegend = False,
        fillcolor = 'chocolate',
        line = dict(color = 'DarkSalmon')))
    
fig2.update_layout(yaxis = dict(range=[0.5,7.5]), title = "Average poo type over whole year", font = dict(size = 16))
fig2.update_yaxes(ticks="inside", tick0 = 1, dtick = 1, title = "Bristol stool scale index")

plot(fig2)

# %% Ridgeline plot for day of week on x axis and type of poo on y axis

# 12 rows of data, one for each month
# 7 columns of data, averaging that months poo types
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

New_Date_column = df['When did the poo occur? '].dt.strftime("%b")
i = 0
max_val = 0
data = np.zeros([12,100]) # the value of 100 is just massively oversizing it, assuming there will be less than 100 poo's of a single type in one month
for month in months:
    for j in range(1,8):
        data[i, np.sum(df['Type of poop 💩? '][New_Date_column == month] == str(j))] = j-1
        if max_val < np.sum(df['Type of poop 💩? '][New_Date_column == month] == str(j)):
            max_val = np.sum(df['Type of poop 💩? '][New_Date_column == month] == str(j))   
    i += 1
    
# Find where the furthest right hand datapoint is and then cut everything off after that
idx = np.arange(max_val+1, 100)
data  = np.delete(data, idx, axis=1)

data[data == 0] = 'nan'

fig3 = go.Figure()

for data_line in data:
    fig3.add_trace(go.Violin(x=data_line))

fig3.update_traces(orientation='h', side='positive', width=2, points=False)
fig3.update_layout(xaxis_showgrid=False, 
                   xaxis_zeroline=False, 
                   xaxis=dict(range=[0,8]), 
                   title = "Average poo type over whole year", 
                   font = dict(size = 16))

plot(fig3)


#%% Violin plot for day of week on x axis and type of poo on y axis broken out month by month

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig4 = make_subplots(rows=2, cols=6, shared_yaxes=True, subplot_titles=(months))

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Date_column = df['When did the poo occur? '].dt.strftime("%a")

row_num = 1
col_num = 0
for month in months:
    col_num += 1
    if col_num > 6:
        col_num = 1
        row_num = 2
    for day in days:
        fig4.add_trace(go.Violin(x = Date_column[Date_column == day][New_Date_column == month],
            y = df['Type of poop 💩? '][Date_column == day][New_Date_column == month],
            name = month + day,
            box_visible = True,
            meanline_visible = True,
            showlegend = False, 
            fillcolor = 'chocolate',
            line = dict(color = 'DarkSalmon')),
            row = row_num, col = col_num)

fig4.update_layout(yaxis = dict(range=[0.5,7.5]), title = "Average poo type, broken down month-by-month", font = dict(size = 16))
fig4.update_yaxes(ticks="inside", col = 1, tick0 = 1, dtick = 1, title = "Bristol stool scale index")
fig4.update_xaxes(ticks="inside")

plot(fig4)

#%% scatter plot x axis = Time since last poo (delta t), y axis (Size of poo)

# Return the number of hours from a timedelta
def days_hours_minutes(td):
    return td.days*24 + td.seconds//3600 + (td.seconds//60)%60/60

d = {'When did the poo occur?': df['When did the poo occur? '], 'Size of poo?': df['Size of poo? '], 'time_since_last_poo': pd.Timedelta(0, unit='h')}
scatterplot_df = pd.DataFrame(data=d)

scatterplot_df = scatterplot_df.sort_values(by = ['When did the poo occur?']).reset_index(drop=True)

for i in range(1, len(df['When did the poo occur? '])-1):
    scatterplot_df.loc[i, 'time_since_last_poo'] = days_hours_minutes(scatterplot_df['When did the poo occur?'][i] - scatterplot_df['When did the poo occur?'][i-1])

scatterplot_df.loc[0, 'time_since_last_poo'] = 0
scatterplot_df.loc[scatterplot_df['time_since_last_poo'].last_valid_index(), 'time_since_last_poo'] = 0

# Correlation line
dataforfitline = np.zeros([np.size(scatterplot_df,0), 1])
j = 0
for i in scatterplot_df['Size of poo?']:
    if i == 'Small':
        dataforfitline[j] = 1
    if i == 'Medium':
        dataforfitline[j] = 2
    if i == 'Poonarmi':
        dataforfitline[j] = 3
    j += 1

dataforfitline2 = pd.DataFrame(data = scatterplot_df['time_since_last_poo'])
dataforfitline2[1] = dataforfitline
dataforfitline2 = dataforfitline2.sort_values(by = ['time_since_last_poo']).reset_index(drop=True)

slope, intercept, r_value, p_value, std_err = stats.linregress(dataforfitline2.astype(float))
line = slope*scatterplot_df['time_since_last_poo'] + intercept

fig5 = go.Figure(data=go.Scatter(x = scatterplot_df['time_since_last_poo'], 
                                 # y = scatterplot_df['Size of poo?'], 
                                 y = dataforfitline2[1],
                                 mode = 'markers', 
                                 text = scatterplot_df['When did the poo occur?'],
                                 name = 'Poops',
                                 hovertemplate = "%{text}"))

fig5.add_trace(go.Scatter(x = scatterplot_df['time_since_last_poo'], y = line, mode = 'lines', name = 'R\u00b2 = ' + round(r_value**2,2).astype(str)))

fig5.update_xaxes(title_text="Hours since last poop")
fig5.update_yaxes(title_text="Size of poop")
fig5.update_layout(title = "Correlation between time since last poo and size of poo", font = dict(size = 16))

plot(fig5)


#%% scatter plot x axis = Time since las poo (delta t), y axis (Type of poo)

d2 = {'When did the poo occur?': df['When did the poo occur? '], 'Type of poo?': df['Type of poop 💩? '], 'time_since_last_poo': pd.Timedelta(0, unit='h')}
scatterplot_df2 = pd.DataFrame(data=d2)

scatterplot_df2 = scatterplot_df2.sort_values(by = ['When did the poo occur?']).reset_index(drop=True)

for i in range(1, len(df['When did the poo occur? '])-1):
    scatterplot_df2.loc[i, 'time_since_last_poo'] = days_hours_minutes(scatterplot_df2['When did the poo occur?'][i] - scatterplot_df2['When did the poo occur?'][i-1])

scatterplot_df2.loc[0, 'time_since_last_poo'] = 0
scatterplot_df2.loc[scatterplot_df2['time_since_last_poo'].last_valid_index(), 'time_since_last_poo'] = 0

# Correlation line
dataforfitline3 = pd.DataFrame(data = scatterplot_df2['time_since_last_poo'])
dataforfitline3[1] = scatterplot_df2['Type of poo?']
dataforfitline3 = dataforfitline3.sort_values(by = ['time_since_last_poo']).reset_index(drop=True)

slope, intercept, r_value, p_value, std_err = stats.linregress(dataforfitline3.astype(float))
line = slope*scatterplot_df2['time_since_last_poo'] + intercept

fig6 = go.Figure(data=go.Scatter(x = scatterplot_df2['time_since_last_poo'], 
                                 y = scatterplot_df2['Type of poo?'], 
                                 mode = 'markers', 
                                 text = scatterplot_df2['When did the poo occur?'],
                                 hovertemplate = "%{text}"))

fig6.add_trace(go.Scatter(x = scatterplot_df2['time_since_last_poo'], y = line, mode = 'lines', name = 'R\u00b2 = ' + round(r_value**2,2).astype(str)))

fig6.update_xaxes(title_text = "Hours since last poop")
fig6.update_yaxes(title_text = "Type of poop")
fig6.update_layout(title = "Correlation between time since last poo and type of poo", font = dict(size = 16))

plot(fig6)

# %% Calendar plot of each day and number of poos, darker colour for more poos

# Number of poos for each day
Num_of_poos = pd.DataFrame()

j = 0
for i in df['When did the poo occur? '].dt.strftime("%x").unique():
    Num_of_poos.loc[j, 'Date'] = i
    Num_of_poos.loc[j, 'Day'] = pd.to_datetime(i).strftime("%d")
    Num_of_poos.loc[j, 'Month'] = pd.to_datetime(i).strftime("%b")
    Num_of_poos.loc[j, 'Count'] = (df['When did the poo occur? '].dt.strftime("%x") == i).sum()
    j += 1

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

total_poos_in_month = []
plot_titles = []
j = 0
for i in months:
    total_poos_in_month.append(int(Num_of_poos['Count'][Num_of_poos['Month'] == i].sum()))
    plot_titles.append(i + '<br>Total poopies = ' + str(total_poos_in_month[j]))
    j += 1

fig7 = make_subplots(rows = 2, cols = 6, shared_yaxes = True, subplot_titles = plot_titles)

year = 2020
row_num = 1
col_num = 0
for month in months:
    col_num += 1
    if col_num > 6:
        col_num = 1
        row_num = 2
    
    MyMonthData = calendar.monthcalendar(2020, strptime(month, '%b').tm_mon)
    z = MyMonthData[::-1]
    
    m = 0
    for i in z:
        n = 0
        for j in i:
            if j == 0:
                z[m].pop(n)
                z[m].insert(n, '')
            elif any((Num_of_poos['Day'] == str(j).zfill(2)) & (Num_of_poos['Month'] == month)) == False:
                z[m].pop(n)
                z[m].insert(n, 0)
            else:
                z[m].pop(n)
                z[m].insert(n, int(Num_of_poos.loc[(Num_of_poos['Day'] == str(j).zfill(2)) & (Num_of_poos['Month'] == month), 'Count']))
            n += 1
        m += 1
    
    name = []
    for a in calendar.Calendar().monthdatescalendar(year, strptime(month, '%b').tm_mon):
        for b in a:
               name.append(b.strftime("%d %b %Y"))
    
    name = np.reshape([inner for inner in name], (len(MyMonthData), 7))
    name = name[::-1]
    
    fig7.add_trace(go.Heatmap(
        x = days,
        y = list(range(len(MyMonthData), 0)),
        z = z,
        meta = name,
        hovertemplate = 'Date: %{meta} <br>Number of poos: %{z}<extra></extra>',
        xgap = 1, ygap = 1,
        zmin = 0, zmax = max(Num_of_poos['Count']), 
#        colorscale = "turbid"),
        colorscale = [
        [0, 'rgb(249, 238, 229)'], # 0 for the prettiness 
        [0.14, 'rgb(249, 230, 217)'], # 0
        [0.29, 'rgb(204, 153, 102)'], # 1
        [0.43, 'rgb(153, 102, 51)'], # 2
        [0.57, 'rgb(115, 77, 38)'], # 3
        [0.71, 'rgb(77, 51, 25)'], # 4
        [1, 'rgb(38, 26, 13)']]), # 5
        row = row_num, col = col_num)

fig7['layout'].update(plot_bgcolor = 'white', 
                      title_text = "Poopy calendar", 
                      yaxis_showticklabels = False, 
                      yaxis7_showticklabels = False, 
                      font = dict(size = 16))


plot(fig7)

# add % of that months poos for each day in hovertemplate

# %% Calendar plot of each day and a function of type/number/size of poos, darker colour for worse poos

# Correlation line
dataforfitline = np.zeros([np.size(scatterplot_df,0), 1])
j = 0
for i in scatterplot_df['Size of poo?']:
    if i == 'Small':
        dataforfitline[j] = 1
    if i == 'Medium':
        dataforfitline[j] = 2
    if i == 'Poonarmi':
        dataforfitline[j] = 3
    j += 1

# Number of poos for each day
Num_type_of_poos = pd.DataFrame()

j = 0
for i in df['When did the poo occur? '].dt.strftime("%x").unique():
    Num_type_of_poos.loc[j, 'Date'] = i
    Num_type_of_poos.loc[j, 'Day'] = pd.to_datetime(i).strftime("%d")
    Num_type_of_poos.loc[j, 'Month'] = pd.to_datetime(i).strftime("%b")
    Num_type_of_poos.loc[j, 'Count'] = (df['When did the poo occur? '].dt.strftime("%x") == i).sum()
    Num_type_of_poos.loc[j, 'Type'] = np.abs(int(df['Type of poop 💩? '][j]) - 4)
    Num_type_of_poos.loc[j, 'Size'] = dataforfitline[j]
    # Num_type_of_poos.loc[j, 'Size'] = df['Size of poo? '][j]
    Num_type_of_poos.loc[j, 'Func_data'] = (Num_type_of_poos.loc[j, 'Count'] + Num_type_of_poos.loc[j, 'Type']) * Num_type_of_poos.loc[j, 'Size']
    j += 1

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#total_poos_in_month = []
#plot_titles = []
#j = 0
#for i in months:
#    total_poos_in_month.append(int(Num_type_of_poos['Count'][Num_type_of_poos['Month'] == i].sum()))
#    plot_titles.append(i + '<br>Total poopies = ' + str(total_poos_in_month[j]))
#    j += 1

fig8 = make_subplots(rows = 2, cols = 6, shared_yaxes = True, subplot_titles = months)

year = 2020
row_num = 1
col_num = 0
for month in months:
    col_num += 1
    if col_num > 6:
        col_num = 1
        row_num = 2
    
    MyMonthData = calendar.monthcalendar(2020, strptime(month, '%b').tm_mon)
    z = MyMonthData[::-1]
    
    m = 0
    for i in z:
        n = 0
        for j in i:
            if j == 0:
                z[m].pop(n)
                z[m].insert(n, '')
            elif any((Num_type_of_poos['Day'] == str(j).zfill(2)) & (Num_type_of_poos['Month'] == month)) == False:
                z[m].pop(n)
                z[m].insert(n, 0)
            else:
                z[m].pop(n)
                z[m].insert(n, int(Num_type_of_poos.loc[(Num_type_of_poos['Day'] == str(j).zfill(2)) & (Num_type_of_poos['Month'] == month), 'Func_data']))
            n += 1
        m += 1
    
    name = []
    for a in calendar.Calendar().monthdatescalendar(year, strptime(month, '%b').tm_mon):
        for b in a:
               name.append(b.strftime("%d %b %Y"))
    
    name = np.reshape([inner for inner in name], (len(MyMonthData), 7))
    name = name[::-1]
    
    fig8.add_trace(go.Heatmap(
        x = days,
        y = list(range(len(MyMonthData), 0)),
        z = z,
        meta = name,
        hovertemplate = 'Date: %{meta} <br>Poo impact: %{z}<extra></extra>',
        xgap = 1, ygap = 1,
        zmin = 0, zmax = max(Num_type_of_poos['Func_data']), 
#        colorscale = "turbid"),
        colorscale = [
        [0, 'rgb(249, 230, 217)'], # 0
        [0.2, 'rgb(204, 153, 102)'], # 1
        [0.4, 'rgb(153, 102, 51)'], # 2
        [0.6, 'rgb(115, 77, 38)'], # 3
        [0.8, 'rgb(80, 54, 28)'], # 4
        [1, 'rgb(38, 26, 13)']]), # 5
        row = row_num, col = col_num)

fig8['layout'].update(plot_bgcolor = 'white', 
                      title_text = "Poopy calendar - Function of number of, size of, and type of poos", 
                      yaxis_showticklabels = False, 
                      yaxis7_showticklabels = False, 
                      font = dict(size = 16))


plot(fig8)

# %% Distribution of poos on stool scale per day

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Date_column = df['When did the poo occur? '].dt.strftime("%a")

Total_poos = len(df['Type of poop 💩? '])
ydata = []
for day in days:
        ydata.append((len(df['Type of poop 💩? '][Date_column == day])/Total_poos)*100)
    
fig9 = go.Figure()    
fig9.add_trace(go.Bar(x = days,
        y = ydata,
        hovertemplate = '%{y:.1f}%<extra></extra>',
        name = day,
        showlegend = False,
        marker_color = ('rgb(166,86,50)')))
    
fig9.update_layout(title = "Poo distribution by day", font = dict(size = 16))
fig9.update_yaxes(range=[0, 20], ticks = "inside", title = "Percentage of poos / %")
fig9.update_xaxes(title = "Day of week")

plot(fig9)


#should make this a stacked bar chart of type of poo stacked with the total number of poos as the overall height. 

#%% Most frequent time of day

timerange = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
X_titles = [t + ':00' for t in timerange]

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Time_column = df['When did the poo occur? '].dt.strftime("%H")

Total_poos = len(df['Type of poop 💩? '])
ydata = []
for t in timerange:
        ydata.append((len(df['Type of poop 💩? '][Time_column == t])/Total_poos)*100)
    
fig10 = go.Figure()    
fig10.add_trace(go.Bar(x = timerange,
        y = ydata,
        hovertemplate = '%{y:.1f}%<extra></extra>',
        showlegend = False,
        marker_color = ('rgb(166,86,50)')))
    
fig10.update_layout(title = "Poo distribution by time", font = dict(size = 16))
fig10.update_yaxes(range=[0, 20], ticks = "inside", title = "Percentage of poos / %")
fig10.update_xaxes(ticks = "inside", title = "Time of day", tickmode = 'array', tickvals = [int(t) for t in timerange], ticktext = X_titles)

plot(fig10)

# %% Distribution by type

Type_of_poop = [str(i) for i in range(1,8)] # 1 to 7

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Total_poos = len(df['Type of poop 💩? '])
ydata = []
for poo in Type_of_poop:
        ydata.append((sum(df['Type of poop 💩? '] == poo)/Total_poos)*100)
    
fig11 = go.Figure()    
fig11.add_trace(go.Bar(x = Type_of_poop,
        y = ydata,
        hovertemplate = '%{y:.1f}%<extra></extra>',
        showlegend = False,
        marker_color = ('rgb(166,86,50)')))
    
fig11.update_layout(title = "Poo distribution by type", font = dict(size = 16))
fig11.update_yaxes(range=[0, 60], ticks = "inside", title = "Percentage of poos / %")
fig11.update_xaxes(title = "Type of poo")

plot(fig11)


# %% Distribution by type excluding Jan and Feb

Type_of_poop = [str(i) for i in range(1,8)] # 1 to 7
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

Total_poos = len(df['Type of poop 💩? '])
ydata = []
for poo in Type_of_poop:
        ydata.append(sum(np.logical_and(df['Type of poop 💩? '] == poo, df['When did the poo occur? '].dt.strftime("%m") > '02')/Total_poos)*100)
    
fig12 = go.Figure()    
fig12.add_trace(go.Bar(x = Type_of_poop,
        y = ydata,
        hovertemplate = '%{y:.1f}%<extra></extra>',
        showlegend = False,
        marker_color = ('rgb(166,86,50)')))
    
fig12.update_layout(title = "Poo distribution by type (excluding Jan and Feb)", font = dict(size = 16))
fig12.update_yaxes(range=[0, 60], ticks = "inside", title = "Percentage of poos / %")
fig12.update_xaxes(title = "Type of poo")

plot(fig12)


# %% Poo: The Musical

# 1812 Overture
p = vlc.MediaPlayer("1812 overture - Cut2.mp3")
p.play()

# Use Rain drop style visulisation 
#def plot_the_poos():
# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

if df['Size of poo? '][0] != 1 and df['Size of poo? '][0] != 2 and df['Size of poo? '][0] != 3:
    df['Size of poo? '].replace(['Small', 'Medium', 'Poonarmi'], [1, 2, 3], inplace = True)
    
df = df.sort_values(by=['When did the poo occur? '], ascending = True)

# Number of poos for each day
Overture_of_poos = pd.DataFrame()

j = 0
for i in df['When did the poo occur? '].dt.strftime("%x").unique():
    Overture_of_poos.loc[j, 'Date'] = i
    Overture_of_poos.loc[j, 'Count'] = (df['When did the poo occur? '].dt.strftime("%x") == i).sum()
    Overture_of_poos.loc[j, 'Poo impact'] = 1
    Poo_type = df['Type of poop 💩? '][df['When did the poo occur? '].dt.strftime("%x") == i]
    Poo_size = df['Size of poo? '][df['When did the poo occur? '].dt.strftime("%x") == i]
    for a in Poo_type.index:
        Overture_of_poos.loc[j, 'Poo impact'] += abs(int(Poo_type[a])-4) * Poo_size[a]
    j += 1



# Fixing random state for reproducibility
np.random.seed(3)


# Create new Figure and an Axes which fills it.
fig = plt.figure(figsize=(7, 6))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1), ax.set_xticks([])
ax.set_ylim(0, 1), ax.set_yticks([])

# Create rain data
n_drops = len(Overture_of_poos)
rain_drops = np.zeros(n_drops, dtype=[('position', float, 2),
                                      ('size',     float, 1),
                                      ('growth',   float, 1),
                                      ('color',    float, 4)])

# Initialize the raindrops in random positions and with random growth rates.
rain_drops['position'] = np.random.uniform(0, 1, (n_drops, 2))


# Construct the scatter which we will update during animation
# as the raindrops develop.
scat = ax.scatter(rain_drops['position'][:, 0], rain_drops['position'][:, 1],
                  s = rain_drops['size'], lw = 0.5, edgecolors = 'white', facecolors = 'white')


#rain_drops['growth'] = 50 # np.random.uniform(50, 200, n_drops)
rain_drops['color'] = (102/255, 51/255, 0, 1)

def update(frame_number):
   
    # Get an index which we can use to re-spawn the oldest raindrop.
    current_index = frame_number % n_drops

    # Make all colors more transparent as time progresses.
    rain_drops['color'][:, 3] -= 0.05 # 1.0/len(rain_drops)
    rain_drops['color'][:, 3] = np.clip(rain_drops['color'][:, 3], 0, 1)

    # Make all circles bigger.
    rain_drops['size'] += rain_drops['growth']

    # Pick a new position for oldest rain drop, resetting its size, color and growth factor.
    rain_drops['position'][current_index] = np.random.uniform(0, 1, 2)
    rain_drops['size'][current_index] = Overture_of_poos['Poo impact'][current_index] * 200
    rain_drops['color'][current_index] = (102/255, 51/255, 0, 1)
    rain_drops['growth'][current_index] = rain_drops['size'][current_index]/10 # np.random.uniform(50, 200)

    # Update the scatter collection, with the new colors, sizes and positions.
    scat.set_edgecolors(rain_drops['color'])
    scat.set_facecolors(rain_drops['color'])
    scat.set_sizes(rain_drops['size'])
    scat.set_offsets(rain_drops['position'])
    
    # New text    
    style = dict(size = 20, color = 'black')
    day_of_month = dt.datetime.strptime(Overture_of_poos['Date'][current_index], '%m/%d/%y').strftime("%d")
    month = dt.datetime.strptime(Overture_of_poos['Date'][current_index], '%m/%d/%y').strftime("%B")
    my_text = ax.text(0.8, 0.05, str(day_of_month) + " " + str(month), ha='center', **style)
    
    plt.pause(0.2) # 54 bpm at 4/4
    
    # Clear old text
    my_text.remove()
    
      
# Construct the animation, using the update function as the animation director.
animation = FuncAnimation(fig, update, interval = 30)    
plt.show()
#%%
p.stop()

#%% Poo stats

# Remove 'Type ' before the number
df['Type of poop 💩? '] = df['Type of poop 💩? '].str.replace('Type ', '')

# Number of poos for each day
Num_type_of_poos = pd.DataFrame()

j = 0
for i in df['When did the poo occur? '].dt.strftime("%x").unique():
    Num_type_of_poos.loc[j, 'Date'] = i
    Num_type_of_poos.loc[j, 'Day'] = pd.to_datetime(i).strftime("%d")
    Num_type_of_poos.loc[j, 'Month'] = pd.to_datetime(i).strftime("%b")
    Num_type_of_poos.loc[j, 'Count'] = (df['When did the poo occur? '].dt.strftime("%x") == i).sum()
    Num_type_of_poos.loc[j, 'Type'] = np.abs(int(df['Type of poop 💩? '][j]) - 4)
    Num_type_of_poos.loc[j, 'Size'] = int(df['Size of poo? '][j])
    Num_type_of_poos.loc[j, 'Func_data'] = (Num_type_of_poos.loc[j, 'Count'] + Num_type_of_poos.loc[j, 'Type']) * Num_type_of_poos.loc[j, 'Size']
    j += 1

# Max number of poos in a day, week, month
Max_poopys = np.max(Num_type_of_poos['Count'])
print('Max poos in a day =', Max_poopys)

# Number of sloppy poonarmi's in the year
Num_sloppy_poonarmis = np.logical_and(Num_type_of_poos['Type'] == 3, Num_type_of_poos['Size'] == 3).sum()
print('Number of sloppy poonarmis in a year =', Num_sloppy_poonarmis)

# Total poos in a year
Total_annual_poos = np.size(Num_type_of_poos, 0)
print('Total poos in a year =', Total_annual_poos)

# Total days without poos

# Create a list of dates in each year
# Remove dates based on if the year is not 2020 and then remove duplicate dates (check order duplicates though)
flat_list = []
for sublist in calendar.Calendar().yeardatescalendar(2020):
    for item3 in sublist:
        for item2 in item3:
            for item in item2:
                if item.strftime("%Y") != '2020':
                    continue
                else:
                    flat_list.append(item)

# Remove duplicates
flat_list = list(dict.fromkeys(flat_list))

# Produce list of dates of poos
new_date_list = []
for i in Num_type_of_poos['Date']:
    new_date_list.append(dt.datetime.strptime(i, '%m/%d/%y').date())


Total_no_poo_days = 0
for i in flat_list:
    if i not in new_date_list:
        Total_no_poo_days += 1

print('Total number of days without a poo =', Total_no_poo_days)

# Total days with 3 or more poos


# Average poo's per day, week, month


# Longest poo streak
Longest_poo_streak = 0
poo_streak = 0
for i in flat_list:
    if i in new_date_list:
        poo_streak += 1
    else:
        poo_streak = 0
    # print(poo_streak)
    if poo_streak > Longest_poo_streak:
        date_of_end = i
        # date_of_start = i
        Longest_poo_streak = poo_streak
        
print('Longest poo streak =', Longest_poo_streak, '   ended =', dt.datetime.strftime(date_of_end, "%d %B %Y"))


# Longest time between poos    
Longest_time_between_poos = dt.timedelta(0)
poo_time = dt.timedelta(0)
prev_time = df['When did the poo occur? '][0]
for i in df['When did the poo occur? '][1::]:
    poo_time = i - prev_time
    prev_time = i
    if poo_time > Longest_time_between_poos:
        date_of_end = i
        Longest_time_between_poos = poo_time
        
print('Longest time between poos =', Longest_time_between_poos, '   ended =', dt.datetime.strftime(date_of_end, "%d %B %Y %H:%M:%S"))

# Shortest time between poos
Shortest_time_between_poos = dt.timedelta(0)
poo_time = dt.timedelta(0)
prev_time = df['When did the poo occur? '][0]
for i in df['When did the poo occur? '][1::]:
    poo_time = i - prev_time
    prev_time = i
    if poo_time < Shortest_time_between_poos:
        date_of_end = i
        Shortest_time_between_poos = poo_time
        if Shortest_time_between_poos.days < 0:
            Shortest_time_between_poos = dt.timedelta(days=0, seconds=Shortest_time_between_poos.seconds, microseconds=Shortest_time_between_poos.microseconds)
        
print('Shortest time between poos =', Shortest_time_between_poos, '   ended =', dt.datetime.strftime(date_of_end, "%d %B %Y %H:%M:%S"))

# Average and median time between poos
poo_time = []
prev_time = df['When did the poo occur? '][0]
for i in df['When did the poo occur? '][1::]:
    poo_time.append(i - prev_time)
    prev_time = i
    
Average_time_between_poos = np.mean(poo_time) 
print('Average time between poos =', Average_time_between_poos)

Median_time_between_poos = np.median(poo_time) 
print('Median time between poos =', Median_time_between_poos)

Mode_time_between_poos = stats.mode(poo_time) 
print('Mode time between poos =', Mode_time_between_poos)

#%% Plot distribution of poos
# x = time between poos in 1 hour time ranges
# y = frequency of poos in time ranges

x_data = range(0, int(max(poo_time).seconds/3600 + max(poo_time).days*24))

# convert the list of timedeltas to hours
pt = []
for j in poo_time:
    pt.append(j.seconds/3600 + j.days*24)

# count how many fall within the hourly time brackets
prev_i = x_data[0]
y_data = []
count = 0
for i in x_data[1::]:
    for j in pt:
        if j < i and j > prev_i:
            count += 1
    y_data.append(count)
    count = 0
    prev_i = i

fig13 = go.Figure()
fig13.add_trace(go.Bar(x = list(x_data),
        y = y_data,
        hovertemplate = '%{y:.1f}%<extra></extra>',
        showlegend = False,
        marker_color = ('rgb(166,86,50)')))
    
fig13.update_layout(title = "Poo distribution by time since last poo", font = dict(size = 16))
fig13.update_yaxes(range=[0, 40], ticks = "inside", title = "Percentage of poos / %")
fig13.update_xaxes(title = "Time since last poo (hours)")

plot(fig13)

#%%
# Change poo musical to show poos scrolling across the screen, up for bigger and worse (impact score) and lower for smaller and better





