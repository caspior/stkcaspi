from flask import Flask,render_template,request,redirect
app = Flask(__name__)

@app.route('/index_stock')
def index_stock():
	return render_template('getdata.html')

@app.route('/plot_stock',methods=['POST'])
def plot_stock():
	import numpy as np
	import pandas as pd
	import requests

	from bokeh.layouts import gridplot
	from bokeh.plotting import figure, output_file, show
	from bokeh.embed import components

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

	ticker = request.form['ticker_stock']
	year = '2020'
	month = '12'

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

	script, div = components(p)

	return render_template('plot.html', script=script, div=div)

@app.route('/')
def index():
    return redirect('/index_stock')
	
if __name__ == '__main__':
    app.run(threaded=True, port=5000)