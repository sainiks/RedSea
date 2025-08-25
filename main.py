from flask import Flask, render_template, request, jsonify
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from flask_caching import Cache
import logging
from functools import lru_cache
import concurrent.futures
import time
import os
import datetime
from dotenv import load_dotenv
import numpy as np

load_dotenv()

nltk.download('vader_lexicon', quiet=True)

app = Flask(__name__)


cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 1800
}
cache = Cache(app, config=cache_config)

reddit = praw.Reddit(client_id=os.environ.get("REDDIT_CLIENT_ID", "wxwayoWo8G2jVR6Z5EzbnQ"),
                      client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
                      user_agent=os.environ.get("REDDIT_USER_AGENT", "SentimentPulse"))

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()

@lru_cache(maxsize=512)
def get_sentiment(text):
    if not text or not isinstance(text, str):
        return 0.0
    scores = sentiment_analyzer.polarity_scores(text)
    return scores['compound']


@cache.memoize(timeout=1800)
def get_reddit_posts(company_name, limit=50):
    try:
        subreddit = reddit.subreddit("all")
        # Sort by new to get recent posts for time series analysis
        posts = list(subreddit.search(company_name, limit=limit, sort='new'))
        return posts
    except Exception as e:
        logger.error(f"Error fetching Reddit data: {e}")
        return []


def analyze_post(post):
    title_sentiment = get_sentiment(post.title)

    post.comments.replace_more(limit=0)
    comments = list(post.comments)[:2]
    comment_sentiments = [get_sentiment(comment.body) for comment in comments if hasattr(comment, 'body')]
    
    avg_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments) if comment_sentiments else 0

    return {
        "title": post.title,
        "title_sentiment": round(title_sentiment, 2),
        "avg_comment_sentiment": round(avg_comment_sentiment, 2),
        "url": post.url,
        "created_utc": post.created_utc # Pass timestamp for time series analysis
    }


def calculate_time_series_sentiment(analyzed_posts, num_intervals=12, interval_minutes=10):
    """Calculate time series sentiment data from actual post times."""
    sentiment_data = []
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Make sure we have posts to analyze
    if not analyzed_posts:
        return []

    for i in range(num_intervals):
        interval_end = now_utc - datetime.timedelta(minutes=i * interval_minutes)
        interval_start = now_utc - datetime.timedelta(minutes=(i + 1) * interval_minutes)
        
        interval_posts = [
            p for p in analyzed_posts 
            if interval_start <= datetime.datetime.fromtimestamp(p['created_utc'], tz=datetime.timezone.utc) < interval_end
        ]
        
        positive = sum(1 for p in interval_posts if p['title_sentiment'] > 0.05)
        negative = sum(1 for p in interval_posts if p['title_sentiment'] < -0.05)
        neutral = sum(1 for p in interval_posts if -0.05 <= p['title_sentiment'] <= 0.05)
        total = len(interval_posts)

        sentiment_data.append({
            "time": interval_start.strftime("%Y-%m-%d %H:%M:%S"),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "total": total
        })

    return sorted(sentiment_data, key=lambda x: x['time'])


@app.route("/sentiment-data")
def sentiment_data():
    company_name = request.args.get("company_name")
    if not company_name:
        return jsonify([])
    
    posts = get_reddit_posts(company_name)
    analyzed_posts = list(map(analyze_post, posts))
    
    time_series_data = calculate_time_series_sentiment(analyzed_posts)
    return jsonify(time_series_data)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_time = time.time()
        company_name = request.form["company_name"]  
        posts = get_reddit_posts(company_name)

        analyzed_posts = []
        if posts:
            chunk_size = 4
            post_chunks = [posts[i:i + chunk_size] for i in range(0, len(posts), chunk_size)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                for chunk in post_chunks:
                    chunk_results = list(executor.map(analyze_post, chunk))
                    analyzed_posts.extend(chunk_results)
        
        # Sort posts by time for display
        analyzed_posts.sort(key=lambda x: x['created_utc'], reverse=True)

        processing_time = round(time.time() - start_time, 2)
        return render_template(
            "index.html",
            company_name=company_name,
            posts=analyzed_posts,
            processing_time=processing_time,
            error_message="" if posts else "No Reddit posts found. Please try another search term."
        )
    return render_template("index.html")

if __name__ == "__main__":
    if not os.environ.get("REDDIT_CLIENT_SECRET"):
        print("WARNING: Reddit client secret not set in environment variables.")
        print("Please create a .env file with your Reddit API credentials.")
        print("See https://www.reddit.com/prefs/apps to create a Reddit app.")

    try:
        app.run(debug=False, threaded=True, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        print(f"Application failed to start: {e}")
