from flask import Flask, render_template, request
from pytrends.request import TrendReq
import os

app = Flask(__name__)

def get_google_trends_data(keyword, timeframe, geo):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
    related_queries = pytrends.related_queries()
    suggestions = pytrends.suggestions(keyword)

    data = {
        'trends': related_queries[keyword]['top']['query'].tolist() if related_queries.get(keyword) else [],
        'suggestions': [suggestion['title'] for suggestion in suggestions]
    }
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find-trends', methods=['POST'])
def find_trends():
    keyword = request.form['keyword']
    timeframe = request.form.get('timeframe', 'today 12-m')
    geo = request.form.get('geo', '')
    trends_data = get_google_trends_data(keyword, timeframe, geo)
    
    # Implement pagination logic here if necessary

    return render_template('results.html', keyword=keyword, trends_data=trends_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
