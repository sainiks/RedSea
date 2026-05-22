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
from praw.exceptions import PrawException
from requests.exceptions import RequestException

load_dotenv()

# Configure a writable directory in /tmp for NLTK in serverless environments (like Vercel)
nltk_data_dir = os.path.join('/tmp', 'nltk_data')
if not os.path.exists(nltk_data_dir):
    try:
        os.makedirs(nltk_data_dir, exist_ok=True)
    except Exception:
        pass

if os.path.exists(nltk_data_dir):
    nltk.data.path.append(nltk_data_dir)

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except (OSError, IOError):
        nltk.download('vader_lexicon', download_dir=nltk_data_dir, quiet=True)


app = Flask(__name__)


cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 1800
}
cache = Cache(app, config=cache_config)

reddit = praw.Reddit(client_id=os.environ.get("REDDIT_CLIENT_ID"),
                      client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
                      user_agent=os.environ.get("REDDIT_USER_AGENT", "RedSea/1.0"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()

@lru_cache(maxsize=512)
def get_sentiment(text):
    if not text or not isinstance(text, str):
        return 0.0
    scores = sentiment_analyzer.polarity_scores(text)
    return scores['compound']


# Tune batch/thread usage parameters for flexibility
DEFAULT_CHUNK_SIZE = 5
DEFAULT_MAX_WORKERS = 4
DEFAULT_COMMENTS_PER_POST = 5

@cache.memoize(timeout=1800)
def get_reddit_posts(company_name, limit=50, max_retries=3):
    """Fetches recent Reddit posts about company_name. Cached at the network level.
    
    Args:
        company_name: The company to search for
        limit: Maximum number of posts to return
        max_retries: Number of retry attempts with exponential backoff
    
    Returns:
        List of Reddit posts or empty list on failure
    """
    for attempt in range(max_retries):
        try:
            subreddit = reddit.subreddit("all")
            posts = list(subreddit.search(company_name, limit=limit, sort='new'))
            return posts
        except (PrawException, RequestException) as e:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logger.warning(f"Attempt {attempt + 1} failed fetching Reddit data: {e}. Retrying in {wait_time}s...")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch Reddit posts after {max_retries} attempts: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching Reddit data: {e}")
            return []
    return []


def analyze_post(post):
    """Analyze sentiment of a post title and a subset of top-level comments."""
    title_sentiment = get_sentiment(post.title)
    post.comments.replace_more(limit=0)
    comments = list(post.comments)[:DEFAULT_COMMENTS_PER_POST]
    comment_sentiments = [get_sentiment(comment.body) for comment in comments if hasattr(comment, 'body')]
    avg_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments) if comment_sentiments else 0
    return {
        "title": post.title,
        "title_sentiment": round(title_sentiment, 2),
        "avg_comment_sentiment": round(avg_comment_sentiment, 2),
        "url": post.url,
        "created_utc": post.created_utc
    }


def calculate_time_series_sentiment(analyzed_posts, num_intervals=12, interval_minutes=10):
    """Calculate time series sentiment data from actual post times."""
    sentiment_data = []
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Make sure we have posts to analyze
    if not analyzed_posts:
        return []

    # Calculate intervals from oldest to newest for proper chronological order
    for i in range(num_intervals):
        # Calculate intervals chronologically (oldest first)
        interval_start = now_utc - datetime.timedelta(minutes=(num_intervals - i) * interval_minutes)
        interval_end = now_utc - datetime.timedelta(minutes=(num_intervals - i - 1) * interval_minutes)
        
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

    # Data is already in chronological order
    return sentiment_data


@app.route("/sentiment-data")
def sentiment_data():
    company_name = request.args.get("company_name")
    if not company_name:
        return jsonify([])
    
    posts = get_reddit_posts(company_name)
    # Fast path for chart updates: title sentiment is sufficient for interval counts.
    analyzed_posts = [
        {
            "title_sentiment": round(get_sentiment(post.title), 2),
            "created_utc": post.created_utc
        }
        for post in posts
    ]
    
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
            chunk_size = DEFAULT_CHUNK_SIZE
            post_chunks = [posts[i:i + chunk_size] for i in range(0, len(posts), chunk_size)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=DEFAULT_MAX_WORKERS) as executor:
                for chunk in post_chunks:
                    chunk_results = list(executor.map(analyze_post, chunk))
                    analyzed_posts.extend(chunk_results)
        # Sort posts by time for display
        analyzed_posts.sort(key=lambda x: x['created_utc'], reverse=True)
        time_series_data = calculate_time_series_sentiment(analyzed_posts)
        processing_time = round(time.time() - start_time, 2)
        return render_template(
            "index.html",
            company_name=company_name,
            posts=analyzed_posts,
            initial_chart_data=time_series_data,
            processing_time=processing_time,
            error_message="" if posts else "No Reddit posts found. Please try another search term."
        )
    return render_template("index.html")

if __name__ == "__main__":
    # Validate required environment variables
    required_env_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file with your Reddit API credentials.")
        print("See https://www.reddit.com/prefs/apps to create a Reddit app.")
        print("\nRequired format in .env:")
        print("  REDDIT_CLIENT_ID=your_client_id")
        print("  REDDIT_CLIENT_SECRET=your_secret")
        print("  REDDIT_USER_AGENT=your_user_agent")
        exit(1)

    try:
        logger.info("Starting RedSea application on http://127.0.0.1:5001")
        app.run(debug=False, threaded=True, host='127.0.0.1', port=5001)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        print(f"Application failed to start: {e}")
        exit(1)
