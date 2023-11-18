from flask import Flask, render_template, request
from pytrends.request import TrendReq
import os  # Import the os module

app = Flask(__name__)

def get_google_trends_data(keyword, timeframe, geo):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo if geo else '', gprop='')
    related_queries = pytrends.related_queries()
    suggestions = pytrends.suggestions(keyword)

    data = {
        'trends': related_queries[keyword]['top']['query'].tolist() if related_queries.get(keyword) else [],
        'suggestions': [suggestion['title'] for suggestion in suggestions]
    }
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    trends_data = None
    if request.method == 'POST':
        keyword = request.form['keyword']
        timeframe = request.form.get('timeframe', 'today 12-m')
        geo = request.form.get('geo', '')
        page = request.args.get('page', 1, type=int)
        trends_data = get_google_trends_data(keyword, timeframe, geo)

        # Pagination
        per_page = 20
        total_keywords = len(trends_data['trends'])
        start = (page - 1) * per_page
        end = start + per_page
        paginated_keywords = trends_data['trends'][start:end]
        total_pages = (total_keywords - 1) // per_page + 1
        trends_data['trends'] = paginated_keywords

        return render_template('results.html', keyword=keyword, trends_data=trends_data, page=page, total_pages=total_pages)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

