from flask import Flask,render_template,request,redirect
app_stock = Flask(__name__)

app_stock.vars={}

@app_stock.route('/index_stock',methods=['GET','POST'])
def index_stock():
	if request.method == 'GET':
		return render_template('getdata.html')
	else:
		app_stock.vars['ticker'] = request.form['ticker_stock']
		#app_stock.vars['year'] = request.form['year_stock']
		#app_stock.vars['month'] = request.form['month_stock']

		f = open('ticker.txt','w')
		f.write(app_stock.vars['ticker'])
		f.close()

		return redirect('/plot_stock')

@app_stock.route('/plot_stock',methods=['GET','POST'])
def plot_stock():
	import numpy as np
	import pandas as pd
	import requests

	from bokeh.layouts import gridplot
	from bokeh.plotting import figure, output_file, show

	def get_stock(ticker,year,month):
		key = '4W96UGLZ59DYW804'
		url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}&outputsize=full'.format(ticker, key)

		response = requests.get(url)
		json = response.json()
		data = json['Time Series (Daily)']

		if month in {'04','06','09','11'}:
			m = 30
		elif month == '02':
			if int(year) % 4 == 0:
				m = 29
			else:
				m = 28
		else:
        		m = 31

		prices = pd.DataFrame(index=range(m),columns=['Date','Adjusted Close'])
    
		for i, row in prices.iterrows():
			if i < 9:
				day = '0' + str(i+1)
			else:
				day = str(i+1)
			key = year+'-'+month+'-'+day
			if key not in data:
				continue
			prices.at[i,'Adjusted Close'] = data[key]['5. adjusted close']
			prices.at[i,'Date'] = key

		prices = prices.dropna()
		stock = {'ticker': ticker, 'year': year, 'month': month, 'prices': prices}
		return stock

	def nix(val, lst):
		return [x for x in lst if x != val]

	f = open("ticker.txt", "r")
	ticker = f.readline()

	#ticker = 'AAPL'
	year = '2020'
	month = '01'

	stk = get_stock(ticker,year,month)

	def datetime(x):
		return np.array(x, dtype=np.datetime64)
	
	months_dict = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June', '07':'July', '08':'August', 	'09':'September', '10':'October', '11':'November', '12':'December'}
	mty = months_dict[month]+' '+year

	p = figure(x_axis_type="datetime", title="Adjusted Closing Prices %s" % mty)
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label = 'Date'
	p.yaxis.axis_label = 'Price (USD)'

	p.line(datetime(stk['prices']['Date']), stk['prices']['Adjusted Close'], color='#DB1111', legend_label=stk['ticker'], width=3)

	st = np.array(stk['prices']['Adjusted Close'])
	st_dates = np.array(stk['prices']['Date'])

	output_file("stock.html", title="Adjusted Closing Prices")
	show(gridplot([[p]], plot_width=400, plot_height=400))
	
if __name__ == '__main__':
    app_stock.run(debug=True)