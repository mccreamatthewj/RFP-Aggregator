import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import the crawler correctly
from crawlers.indiana_crawler import IndianaCrawler

# The rest of your code...
