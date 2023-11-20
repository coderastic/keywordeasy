from flask import Flask, render_template, request
from pytrends.request import TrendReq
import requests
import os

app = Flask(__name__)

def get_proxy_from_scraperapi():
    scraperapi_key = 'abe166316c156f08bb343bd4ed5c08be'
    target_url = 'https://trends.google.com'

    payload = {'api_key': scraperapi_key, 'url': target_url}
    response = requests.get('http://api.scraperapi.com', params=payload)

    if response.status_code == 200:
        return response.text.strip()
    else:
        return None

def get_google_trends_data(keyword, timeframe, geo):
    proxy = get_proxy_from_scraperapi()
    if proxy:
        pytrends = TrendReq(hl='en-US', tz=360, proxies={'https': proxy})
    else:
        pytrends = TrendReq(hl='en-US', tz=360)

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
        return {'error': str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/find-trends', methods=['GET', 'POST'])
def find_trends():
    keyword = request.args.get('keyword') if request.method == 'GET' else request.form['keyword']
    timeframe = request.args.get('timeframe', 'today 12-m') if request.method == 'GET' else request.form.get('timeframe', 'today 12-m')
    geo = request.args.get('geo', '') if request.method == 'GET' else request.form.get('geo', '')
    
    trends_data = get_google_trends_data(keyword, timeframe, geo)
    if 'error' in trends_data:
        return render_template('error.html', error=trends_data['error'])

    # Pagination logic
    items_per_page = 20
    total_items = len(trends_data['trends'])
    total_pages = (total_items + items_per_page - 1) // items_per_page
    page = request.args.get('page', 1, type=int)

    return render_template('results.html', keyword=keyword, trends_data=trends_data, total_pages=total_pages, page=page)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)



