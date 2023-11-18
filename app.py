from flask import Flask, render_template, request
from pytrends.request import TrendReq
import os
import pytrends.exceptions

app = Flask(__name__)

def get_google_trends_data(keyword, timeframe, geo):
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
    except pytrends.exceptions.TooManyRequestsError:
        return {'trends': [], 'suggestions': [], 'error': 'Too many requests. Please try again later.'}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/find-trends', methods=['GET', 'POST'])
def find_trends():
    keyword = request.args.get('keyword') if request.method == 'GET' else request.form['keyword']
    timeframe = request.args.get('timeframe', 'today 12-m') if request.method == 'GET' else request.form.get('timeframe', 'today 12-m')
    geo = request.args.get('geo', '') if request.method == 'GET' else request.form.get('geo', '')
    page = request.args.get('page', 1, type=int)

    trends_data = get_google_trends_data(keyword, timeframe, geo)
    if 'error' in trends_data:
        return render_template('error.html', error=trends_data['error'])

    # Pagination Logic
    per_page = 20
    total_keywords = len(trends_data['trends'])
    start = (page - 1) * per_page
    end = start + per_page
    paginated_keywords = trends_data['trends'][start:end]
    total_pages = (total_keywords - 1) // per_page + 1

    return render_template('results.html', keyword=keyword, trends_data=trends_data, page=page, total_pages=total_pages, suggestions=trends_data['suggestions'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
