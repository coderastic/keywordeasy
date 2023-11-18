from flask import Flask, render_template, request
from pytrends.request import TrendReq

app = Flask(__name__)

def get_google_trends_keywords(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
    related_queries = pytrends.related_queries()
    return related_queries[keyword]['top']['query'].tolist() if related_queries.get(keyword) else []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find-trends', methods=['POST'])
def find_trends():
    keyword = request.form['keyword']
    trends_keywords = get_google_trends_keywords(keyword)
    return render_template('results.html', keyword=keyword, trends=trends_keywords)

if __name__ == '__main__':
    app.run(debug=True)
