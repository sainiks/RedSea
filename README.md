# RedSea

An ultra-modern, real-time sentiment monitoring dashboard designed to capture the immediate emotional pulse of online discussions. Enter any company, product, or search term and instantly visualize public opinion.

---

## 🎯 What RedSea is For

In today’s fast-paced digital ecosystem, public opinion shifts in minutes. **RedSea** acts as an early warning system and trend radar. It is designed for:
- **Brand Reputation Tracking**: Monitor public sentiment surrounding product launches, PR events, or company announcements.
- **Market Research**: Uncover organic, community-driven opinions about competitors and industry trends.
- **Financial & Social Sentiment Analysis**: Visualize retail investor sentiment and general enthusiasm surrounding stocks, crypto assets, or brands.
- **Audience Feedback Aggregation**: Help creators, developers, and organizations see how users really feel about their work.

---

## ✨ Key Features (What It Does)

- **Instant Search**: Type in any topic or company name (e.g., *Tesla, Apple, Google*) to start.
- **Dynamic Sentiment Distribution**: Automatically analyzes and scores public opinions into distinct **Positive**, **Negative**, and **Neutral** categories.
- **Interactive Sentiment Charting**: Projects sentiment trends onto a beautiful, interactive line chart to track temporal shifts in real time.
- **Smart Background Polling**: Updates the chart in real time while you work. It is designed to pause automatically when you minimize or switch tabs to save resources.
- **Granular Post-Level Breakdown**: Displays individual cards for analyzed posts, featuring standalone sentiment indicator badges and colored highlight borders.
- **Premium User Experience**: Packed with micro-animations, slide-up panels, loading states, and a liquid-inspired dark theme.
- **Responsive Layout**: Works seamlessly across desktops, tablets, and mobile devices.

---

## 🚀 Getting Started

Follow these steps to run your own local instance of the RedSea dashboard.

### Prerequisites
- **Python 3.8** or higher
- **pip** (Python package installer)

### Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://your-repo-link.git
   cd RedSea
   ```

2. **Set up a virtual environment** (highly recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your credentials:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=RedSea
   ```
   *(Create a developer application at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) to obtain your credentials.)*

### Running the Dashboard

Launch the application using:
```bash
python app.py
```
Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your web browser to access the dashboard.

---

## 🧪 Testing

To run the automated test suite:
```bash
pytest unit_test.py
```
