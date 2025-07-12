from flask import Flask, render_template, request, jsonify
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from flask_caching import Cache
import logging
from functools import lru_cache
import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

matplotlib.style.use('fast')  # Use faster style for plots
import io
import base64
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
    'CACHE_TYPE': 'simple',  # Change to 'redis' in production
    'CACHE_DEFAULT_TIMEOUT': 1800  # Increased from 300s to 1800s (30 min)
}
cache = Cache(app, config=cache_config)

# Configure Reddit client once at startup with environment variables
reddit = praw.Reddit(client_id=os.environ.get("REDDIT_CLIENT_ID", "wxwayoWo8G2jVR6Z5EzbnQ"),
                      client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
                      user_agent=os.environ.get("REDDIT_USER_AGENT", "SentimentPulse"))

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer once and reuse
sentiment_analyzer = SentimentIntensityAnalyzer()

# Pre-compile frequently used computations with increased cache size
@lru_cache(maxsize=512)  # Increased from default
def get_sentiment(text):
    """Analyze sentiment of text using VADER (much faster than TextBlob)"""
    if not text or not isinstance(text, str):
        return 0.0

    # VADER is optimized for social media text
    scores = sentiment_analyzer.polarity_scores(text)
    return scores['compound']  # Returns a value between -1 and 1


@cache.memoize(timeout=1800)  # cache for 30 min
def get_reddit_posts(company_name, limit=50):
    try:
        subreddit = reddit.subreddit("all")
        posts = list(subreddit.search(company_name, limit=limit))
        return posts
    except Exception as e:  # Handle errors during Reddit API interaction
        logger.error(f"Error fetching Reddit data: {e}")
        return []


def analyze_post(post):
    """Analyze a single post and its comments with optimized processing"""
    title_sentiment = get_sentiment(post.title)

    # Process only top 2 comments instead of 3 for better performance
    post.comments.replace_more(limit=0)
    comments = list(post.comments)[:2]
    comment_sentiments = [get_sentiment(comment.body) for comment in comments if hasattr(comment, 'body')]
    
    avg_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments) if comment_sentiments else 0

    return {
        "title": post.title,
        "title_sentiment": round(title_sentiment, 2),
        "avg_comment_sentiment": round(avg_comment_sentiment, 2),
        "url": post.url
    }


def calculate_time_series_sentiment(analyzed_posts, interval_seconds=60):
    """Calculate time series sentiment data."""
    now = datetime.datetime.now()
    # Create time intervals
    time_intervals = [(now - datetime.timedelta(seconds=i * interval_seconds)).strftime("%Y-%m-%d %H:%M:%S")
                      for i in range(10, -1, -1)]

    sentiment_data = {interval: {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
                      for interval in time_intervals}

    for post in analyzed_posts:
        post_time_offset = np.random.randint(0, interval_seconds * len(time_intervals))  # Simulate comment times within the entire range of intervals
        post_time = now - datetime.timedelta(seconds=post_time_offset)
        # Find the correct time interval for this post
        for i, interval in enumerate(time_intervals):
            interval_start = now - datetime.timedelta(seconds=i * interval_seconds)
            interval_end = now - datetime.timedelta(seconds=(i + 1) * interval_seconds)
            if interval_end <= post_time < interval_start:
                time_key = interval
                break
        else:
            continue
        if time_key in sentiment_data:  # Ensure we only use one interval
            sentiment_value = post["title_sentiment"]
            sentiment_data[time_key]["positive"] += int(sentiment_value > 0)
            sentiment_data[time_key]["negative"] += int(sentiment_value < 0)
            sentiment_data[time_key]["neutral"] += int(sentiment_value == 0)
            sentiment_data[time_key]["total"] += 1
    
    return [{"time": interval, **data} for interval, data in sentiment_data.items() if data["total"] > 0]


@lru_cache(maxsize=128)
def create_sentiment_plot(pos_pct, neg_pct, neu_pct):
    if any(not isinstance(x, (int, float)) or np.isnan(x) for x in [pos_pct, neg_pct, neu_pct]):
        pos_pct = neg_pct = neu_pct = 33.33

    if pos_pct + neg_pct + neu_pct == 0:
        pos_pct = neg_pct = neu_pct = 33.33
    fig, ax = plt.subplots(figsize=(4, 4), dpi=72)
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [pos_pct, neg_pct, neu_pct]
    colors = ['#92D050', '#FF0000', '#FFFF00']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', 
                pad_inches=0.1, transparent=False)
    plt.close(fig)  # Close to free memory

    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()


@app.route("/sentiment-data")
def sentiment_data():
    company_name = request.args.get("company_name")
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

        # Calculate sentiment stats
        positive_count = sum(1 for post in analyzed_posts if post["title_sentiment"] > 0)
        negative_count = sum(1 for post in analyzed_posts if post["title_sentiment"] < 0)
        neutral_count = len(analyzed_posts) - positive_count - negative_count

        total_posts = len(analyzed_posts)
        if total_posts > 0:
            positive_percent = (positive_count / total_posts) * 100
            negative_percent = (negative_count / total_posts) * 100
            neutral_percent = (neutral_count / total_posts) * 100
        else:
            positive_percent = negative_percent = neutral_percent = 33.33

        try:
            plot_url = create_sentiment_plot(positive_percent, negative_percent, neutral_percent)
        except Exception as e:  # Handle plot creation errors
            logger.error(f"Error creating plot: {e}")
            # Provide a fallback empty plot
            plot_url = ""

        processing_time = round(time.time() - start_time, 2)
        return render_template(
            "index.html",
            company_name=company_name,
            posts=analyzed_posts,
            plot_url=plot_url,
            processing_time=processing_time,
            error_message="" if posts else "No Reddit posts found. Please try another search term."
        )
    return render_template("index.html")

if __name__ == "__main__":

    # Fix for Reddit API authentication
    if not os.environ.get("REDDIT_CLIENT_SECRET"):
        print("WARNING: Reddit client secret not set in environment variables.")
        print("Please create a .env file with your Reddit API credentials.")
        print("See https://www.reddit.com/prefs/apps to create a Reddit app.")

    try:
        app.run(debug=False, threaded=True, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        print(f"Application failed to start: {e}")
