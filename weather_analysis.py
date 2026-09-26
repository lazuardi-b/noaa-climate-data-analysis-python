# Libraries
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

# EXTRACT & LOAD DATA

# Fetch API data
url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
headers = {"token": "YOUR_TOKEN"}
params = {
    "datasetid": "GHCND",
    "stationid": "GHCND:USW00094789",
    "datatypeid": "PRCP,SNOW,SNWD,TAVG,TMAX,TMIN",
    "startdate": "2026-01-01",
    "enddate": date.today().isoformat(),
    "units": "metric",
    "limit": 1000
}

r = requests.get(url, params=params , headers=headers)
print(r.status_code)

response_dicts = r.json()
print(response_dicts.keys())
print(response_dicts['metadata'])

response_dict = response_dicts['results']
print(len(response_dict))

# Fetch second batch of data, due to limit: 1000
params['offset'] = 1001

r2 = requests.get(url, params=params, headers=headers)
print(r2.status_code)

response_dicts_2 = r2.json()
print(response_dicts_2['metadata'])

response_dict_2 = response_dicts_2['results']
print(len(response_dict_2))

# Combine both fetched data
response_dict = response_dict + response_dict_2
print(len(response_dict))

# TRANSFORM DATA

# pandas data frame (df)
df = pd.DataFrame(response_dict)

# Inspect
print(df.head())
print(df.info())
print(df.shape)
print(df.dtypes)
print(df.columns)
print(df['datatype'].unique())
print(df['datatype'].value_counts())

# date datatype still str, need to be datetime
df['date'] = pd.to_datetime(df['date'])

# create df copy to work with
df_clean = df.copy()

# inspect
print(df_clean.head())
print(df_clean.info())
print(df_clean['date'].max())
print(df_clean['date'].min())
print(df_clean['date'].nunique())
print(df_clean['datatype'].unique())
print(df_clean['datatype'].value_counts())

# drop the column we don't need
df_clean = df_clean.drop(columns=['station', 'attributes'])

# pivot from long to wide format
df_clean = df_clean.pivot(
    columns='datatype',
    index='date',
    values='value'
).reset_index()

# inspect
print(df_clean.head())
print(df_clean.info())
print(df_clean.isna().sum())
print(df_clean.describe())

# VISUALIZE DATA

# Daily High vs Low Temperature
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots()
ax.plot(df_clean['date'], df_clean['TMAX'], color='red', linewidth=1)
ax.plot(df_clean['date'], df_clean['TMIN'], color='blue', linewidth=1)

ax.fill_between(df_clean['date'], df_clean['TMAX'], df_clean['TMIN'], facecolor='blue', alpha=0.1)

ax.set_title("Daily High and Low Temperature, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
ax.set_ylabel("Temperature (\u00b0C)", fontsize=12)
ax.tick_params(labelsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.legend(['Daily High', 'Daily Low'], fontsize=8, loc='upper right')

ax.set_xlim(df_clean['date'].min() - pd.Timedelta(days=3), df_clean['date'].max())

max_temp = df_clean['TMAX'].max()
min_temp = df_clean['TMIN'].min()
max_date = df_clean.loc[df_clean['TMAX'].idxmax(), "date"]
min_date = df_clean.loc[df_clean['TMIN'].idxmin(), "date"]

ax.scatter(x=max_date, y=max_temp, c='black', edgecolors='none', s=36, zorder=3)
ax.scatter(x=min_date, y=min_temp, c='black', edgecolors='none', s=36, zorder=3)

ax.annotate(
    f"{max_temp:.1f}\u00b0C",
    xy=(max_date, max_temp),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)
ax.annotate(
    f"{min_temp:.1f}\u00b0C",
    xy=(min_date, min_temp),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)

fig.savefig("charts/tmax_tmin.png", dpi=150)
plt.show()

# Daily Rainfall
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots()
ax.plot(df_clean['date'], df_clean['PRCP'], color='blue', linewidth=1)

ax.set_title("Daily Rainfall, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
ax.set_ylabel("Precipitation (mm)", fontsize=12)
ax.tick_params(labelsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

ax.set_xlim(df_clean['date'].min() - pd.Timedelta(days=3), df_clean['date'].max())

max_rain = df_clean['PRCP'].max()
max_date = df_clean.loc[df_clean['PRCP'].idxmax(), "date"]
ax.scatter(x=max_date, y=max_rain, c='red', edgecolors='none', s=36, zorder=3)

ax.annotate(
    f"{max_rain:.1f}mm",
    xy=(max_date, max_rain),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)

fig.savefig("charts/prcp.png", dpi=150)
plt.show()

# Daily Snowfall & Snow Depth
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots(1, 2, sharey=True)

ax[0].plot(df_clean['date'], df_clean['SNOW'], color='deepskyblue', linewidth=1)
ax[1].plot(df_clean['date'], df_clean['SNWD'], color='blue', linewidth=1)

ax[0].set_title("Daily Snowfall")
ax[0].set_ylabel("depth (mm)")

max_snow = df_clean['SNOW'].max()
max_date_snow = df_clean.loc[df_clean['SNOW'].idxmax(), "date"]
ax[0].scatter(x=max_date_snow, y=max_snow, c='red', edgecolors='none', s=36, zorder=3)
ax[0].annotate(f"{max_snow:.1f} mm", xy=(max_date_snow, max_snow), xytext=(5, 0), textcoords="offset points", fontsize=8)

ax[1].set_title("Daily Snow Depth")

max_snwd = df_clean['SNWD'].max()
max_date_snwd = df_clean.loc[df_clean['SNWD'].idxmax(), "date"]
ax[1].scatter(x=max_date_snwd, y=max_snwd, c='red', edgecolors='none', s=36, zorder=3)
ax[1].annotate(f"{max_snwd:.1f} mm", xy=(max_date_snwd, max_snwd), xytext=(5, 0), textcoords="offset points", fontsize=8)

for a in ax:
    a.xaxis.set_major_locator(mdates.MonthLocator())
    a.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    a.set_xlim(df_clean['date'].min() - pd.Timedelta(days=3), df_clean['date'].max())
    a.tick_params(axis='x', rotation=30, labelsize=8)
    a.tick_params(axis='y', labelsize=8)

fig.suptitle("Daily Snowfall vs Snow Depth, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
fig.tight_layout()

fig.savefig("charts/snow_snwd.png", dpi=150)
plt.show()

