# Test Crawler Script

"""
This script is designed to test the Indiana crawler without requiring authentication credentials.
"""

import requests

# Example test function to check the crawler's functionality
def test_indiana_crawler():
    url = 'http://example.com/crawler-endpoint'  # Replace with the actual endpoint
    response = requests.get(url)
    if response.status_code == 200:
        print('Crawler is working correctly.')
    else:
        print('Crawler failed with status code:', response.status_code)

if __name__ == '__main__':
    test_indiana_crawler()