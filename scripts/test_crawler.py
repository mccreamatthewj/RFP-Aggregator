#!/usr/bin/env python3
"""
Simple test script to verify the Indiana crawler works.
This requires no credentials or environment variables.
"""
import sys
from crawlers.indiana_crawler import IndianaCrawler

def main():
    print("=" * 60)
    print("Testing Indiana RFP Crawler")
    print("=" * 60)
    print()
    
    print("Initializing crawler...")
    crawler = IndianaCrawler()
    
    print("Fetching RFP opportunities from Indiana...")
    try:
        items = crawler.run()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return 1
    
    print()
    if not items:
        print("⚠️  No items found. The Indiana website may be down or the page structure changed.")
        return 0
    
    print(f"✅ Successfully found {len(items)} RFP opportunity(ies)!")
    print()
    
    # Display first few items
    for i, item in enumerate(items[:3], 1):
        print(f"--- Item #{i} ---")
        print(f"Title:       {item.get('title', 'N/A')}")
        print(f"Event ID:    {item.get('event_id', 'N/A')}")
        print(f"Agency:      {item.get('agency', 'N/A')}")
        print(f"Due Date:    {item.get('due_date', 'N/A')}")
        print(f"URL:         {item.get('url', 'N/A')}")
        print(f"Contact:     {item.get('contact_email', 'N/A')}")
        print() 
    
    if len(items) > 3:
        print(f"... and {len(items) - 3} more items")
    
    print("=" * 60)
    print("✅ Crawler test completed successfully!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())