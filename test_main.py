import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, render_template_string
from main import app, create_sentiment_plot  # Import your Flask app and create_sentiment_plot

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def mock_reddit_posts(company_name, limit=20):
    # Create mock post objects

    class MockComments:
        def __init__(self, comments):
            self.comments = comments

        def replace_more(self, limit=None):
            
            pass  # Mock the replace_more method
        
        def __iter__(self):
            for comment in self.comments:
                yield comment
                
    class MockPost:
        def __init__(self, title, url, comments):
            self.title = title
            self.url = url       
            self.comments = MockComments(comments)

    class MockComment:
        def __init__(self, body):
            self.body = body

        def __repr__(self):
            return f"<{self.__class__.__name__} body=\'{self.body}\'>"

    mock_posts = [
        MockPost(title=f"Positive news about {company_name}", url="url1", 
                 comments=[MockComment("Great!")]),
        MockPost(title=f"Negative news about {company_name}", url="url2", 
                 comments=[MockComment("Bad")]),
        MockPost(title=f"Neutral news about {company_name}", url="url3", 
                 comments=[MockComment("Okay")]),
    ]
    return mock_posts[:limit]

@patch('main.get_reddit_posts', side_effect=mock_reddit_posts)
def test_index_route_get(mock_get_reddit_posts, client):
    response = client.get("/")
    assert response.status_code == 200 
    decoded_data = response.data.decode("utf-8")
    print(decoded_data)
    assert '<input\n                            type="text"\n                            name="company_name"\n                            id="company_name"\n                            required\n                            value=""\n                            class="modern-input"\n                            placeholder="Tesla, Apple, Google"\n                        />' in decoded_data


@patch('main.get_reddit_posts', side_effect=mock_reddit_posts)
def test_index_route_post(mock_get_reddit_posts, client):
    response = client.post('/', data={'company_name': 'TestCompany'})
    assert response.status_code == 200
    assert b"TestCompany" in response.data  # Check if company name is in the response
    assert b"Positive" in response.data
    assert b"Negative" in response.data
    assert b"Neutral" in response.data
    mock_get_reddit_posts.assert_called_once_with('TestCompany')

def test_create_sentiment_plot():
    # Test with valid data
    plot_url = create_sentiment_plot(50, 30, 20)
    assert isinstance(plot_url, str)
    assert len(plot_url) > 0

    # Test with invalid data (should return a default or error state)
    plot_url_invalid = create_sentiment_plot("invalid", -10, None)
    assert isinstance(plot_url_invalid, str)
    assert len(plot_url_invalid) > 0  # Should handle gracefully

    # Test with zero values
    plot_url_zero = create_sentiment_plot(0, 0, 0)
    assert isinstance(plot_url_zero, str)
    assert len(plot_url_zero) > 0  # Should handle gracefully
    