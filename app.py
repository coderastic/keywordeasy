from flask import Flask, render_template, request
from pytrends.request import TrendReq
import requests
import random

app = Flask(__name__)

def is_proxy_live(proxy):
    try:
        test_url = 'http://www.google.com'
        response = requests.get(test_url, proxies={'https': proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_live_proxies():
    api_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=250&country=all&ssl=all&anonymity=all'
    response = requests.get(api_url)
    proxy_list = response.text.strip().split('\n')
    return [proxy for proxy in proxy_list if is_proxy_live(proxy)]

def get_google_trends_data(keyword, timeframe, geo, proxies):
    proxy = {'https': random.choice(proxies)} if proxies else None
    pytrends = TrendReq(hl='en-US', tz=360, proxies=proxy)
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo if geo else '', gprop='')
        related_queries = pytrends.related_queries()
        suggestions = pytrends.suggestions(keyword)

        trends = []
        if related_queries.get(keyword) and 'top' in related_queries[keyword]:
            trends = related_queries[keyword]['top']['query'].tolist()

        data = {
            'trends': trends,
            'suggestions': [suggestion['title'] for suggestion in suggestions]
        }
        return data
    except Exception as e:
        return {'trends': [], 'suggestions': [], 'error': str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/find-trends', methods=['GET', 'POST'])
def find_trends():
    keyword = request.args.get('keyword') if request.method == 'GET' else request.form['keyword']
    timeframe = request.args.get('timeframe', 'today 12-m') if request.method == 'GET' else request.form.get('timeframe', 'today 12-m')
    geo = request.args.get('geo', '') if request.method == 'GET' else request.form.get('geo', '')
    proxies = get_live_proxies()

    trends_data = get_google_trends_data(keyword, timeframe, geo, proxies)
    if 'error' in trends_data:
        return render_template('error.html', error=trends_data['error'])

    # (Add your pagination logic here)

    return render_template('results.html', keyword=keyword, trends_data=trends_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
