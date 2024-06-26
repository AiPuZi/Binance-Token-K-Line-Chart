from flask import Flask, render_template, request
import pandas as pd
import requests
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

# 获取币安K线数据
def get_klines(symbol, interval='1d', limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time', 'quote_asset_volume', 'number_of_trades',
                                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df[['open', 'high', 'low', 'close']].astype(float)

# 生成交互式K线图
def create_plot(symbol):
    df = get_klines(symbol)
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])
    fig.update_layout(
        title=f'{symbol} Interactive K-Line',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )
    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

@app.route('/', methods=['GET', 'POST'])
def index():
    chart = None
    if request.method == 'POST':
        symbol = request.form['symbol']
        chart = create_plot(symbol)
    return render_template('index.html', chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
