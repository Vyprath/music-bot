import requests
import datetime
import json
#this block is to get the data from the web
data = requests.get(r'https://www.quandl.com/api/v3/datasets/TC1/INFY.json?api_key=x6R2G8LXKZCzNqh-rkcu')
content = json.loads(data.text)
dictYear = dict()

#gets the closing stock price and the years
for data in content['dataset']['data']:
	year = datetime.datetime.strptime(data[0], '%Y-%m-%d' ).year
	cStock = float(data[5])
	if year not in dictYear:
		dictYear[year] = list() 
		dictYear[year].append(cStock)
	else:
		dictYear[year].append(cStock)

#calculating the average
avg=[]
for year in range(2000, 2011):
  yr_avg = sum(dictYear[year]) / len(dictYear[year])
  print(year, yr_avg)
  avg.append(yr_avg)

