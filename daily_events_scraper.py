#!/usr/bin/env python3
"""
Daily Events Scraper - Get events for specific dates from Pensacola tourism sites
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
import argparse

class DailyEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })

    def get_events_for_date(self, target_date):
        """Get events for a specific date"""
        print(f"🗓️  Searching for events on: {target_date}")

        all_events = []

        # Check both page 1 and page 2 for paginated results
        for page in [1, 2]:
            if page == 1:
                base_url = f"https://www.visitpensacola.com/events/?range=1&date-from={target_date}&date-to={target_date}&categories=544740%2C544743%2C544744%2C544746%2C544751%2C544752%2C2581955%2C7639914&regions=&keyword=&calendar=1"
            else:
                base_url = f"https://www.visitpensacola.com/events/?page={page}&range=1&date-from={target_date}&date-to={target_date}&categories=544740%2C544743%2C544744%2C544746%2C544751%2C544752%2C2581955%2C7639914&regions=&keyword=&calendar=1"

            events = self.scrape_events_from_url(base_url, target_date)
            all_events.extend(events)

        # Filter events to exact date match and deduplicate
        filtered_events = []
        seen = set()

        for event in all_events:
            if event.get('date') == target_date:
                # Create deduplication key
                key = (event.get('title', '').strip(), event.get('link', ''))
                if key not in seen:
                    seen.add(key)
                    filtered_events.append(event)

        return filtered_events

    def scrape_events_from_url(self, url, target_date):
        """Scrape events from a specific URL"""
        events = []

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all event links (more direct approach)
            event_links = soup.find_all('a', href=lambda x: x and '/events/' in x)

            processed_links = set()

            for link in event_links:
                href = link.get('href', '')
                title = link.get_text().strip()

                # Look specifically for "Learn More" links on event cards
                if (href not in processed_links and
                    title and
                    'learn more' in title.lower()):

                    processed_links.add(href)
                    event = self.extract_simple_event_details(link, href, url, target_date)
                    if event:
                        events.append(event)

        except Exception as e:
            print(f"❌ Error scraping URL {url}: {e}")

        # Deduplicate events by title and link
        unique_events = []
        seen = set()

        for event in events:
            # Create a key based on title and link for deduplication
            key = (event.get('title', '').strip(), event.get('link', ''))
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return unique_events

    def extract_simple_event_details(self, link, href, base_url, target_date):
        """Extract event details from a link element based on card structure: Logo, date, title, location, learn more link, location link"""
        try:
            # Get full URL
            if href.startswith('http'):
                event_link = href
            elif href.startswith('/'):
                event_link = urljoin(base_url, href)
            else:
                event_link = urljoin(base_url, '/' + href)

            # Find the parent card container
            card = link.find_parent('article') or link.find_parent('div', class_='card')
            if not card:
                return None

            # Extract title (usually in h3, h2, or h1 element)
            title_elem = card.find('h3') or card.find('h2') or card.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Unknown Event"

            # Extract date from card text - look for "September 18" pattern
            card_text = card.get_text()
            event_date = self.parse_event_date(card_text)

            # Extract location from card text (look for location patterns)
            location = "Pensacola"
            if "downtown pensacola" in card_text.lower():
                location = "Downtown Pensacola"
            elif "pensacola beach" in card_text.lower():
                location = "Pensacola Beach"
            elif "downtown" in card_text.lower():
                location = "Downtown Pensacola"
            elif "beach" in card_text.lower():
                location = "Pensacola Beach"

            return {
                'title': title,
                'date': event_date,
                'time': "",  # Will be filled later if needed
                'location': location,
                'description': title,  # Use title as fallback description
                'category': "Event",
                'link': event_link,
                'source': 'visitpensacola.com'
            }

        except Exception as e:
            print(f"⚠️  Error extracting event details: {e}")
            return None

    def extract_event_details(self, card, base_url):
        """Extract detailed information from an event card"""
        try:
            # Event title and link
            title_elem = card.find('h3') or card.find('h2') or card.find(['a'], href=True)
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Event"

            # Event detail link
            link_elem = card.find('a', href=True)
            event_link = ""
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('http'):
                    event_link = href
                elif href.startswith('/'):
                    event_link = urljoin(base_url, href)
                else:
                    event_link = urljoin(base_url, '/' + href)

            # Date extraction - try specific date element first, then full card text
            date_text = ""
            date_elem = card.find(class_=re.compile(r'date|time')) or card.find('time')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
            else:
                # If no specific date element, use the entire card text
                date_text = card.get_text()

            # Parse date to standard format
            event_date = self.parse_event_date(date_text)

            # Location
            location = "Pensacola"
            location_elem = card.find(class_=re.compile(r'location|venue|address'))
            if location_elem:
                location = location_elem.get_text(strip=True)
            elif "beach" in title.lower() or "beach" in card.get_text().lower():
                location = "Pensacola Beach"
            elif "downtown" in title.lower() or "downtown" in card.get_text().lower():
                location = "Downtown Pensacola"

            # Time
            time_text = ""
            time_elem = card.find(class_=re.compile(r'time')) or card.find('time')
            if time_elem:
                time_match = re.search(r'(\\d{1,2}[:\\s]*\\d{0,2}\\s*[APMapm]{0,2})', time_elem.get_text())
                if time_match:
                    time_text = time_match.group(1).strip()

            # Description
            description = ""
            desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|content|summary'))
            if desc_elem:
                description = desc_elem.get_text(strip=True)[:300]  # Limit description length

            # Category/Type
            category = "Event"
            category_elem = card.find(class_=re.compile(r'category|tag|type'))
            if category_elem:
                category = category_elem.get_text(strip=True)

            return {
                'title': title,
                'date': event_date,
                'time': time_text,
                'location': location,
                'description': description,
                'category': category,
                'link': event_link,
                'source': 'visitpensacola.com'
            }

        except Exception as e:
            print(f"⚠️  Error extracting event details: {e}")
            return None

    def parse_event_date(self, date_text):
        """Parse various date formats to YYYY-MM-DD"""
        if not date_text:
            return ""

        # Try to extract date patterns
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2025-09-18
            r'(\d{2})/(\d{2})/(\d{4})',  # 09/18/2025
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 9/18/2025
        ]

        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if '/' in pattern:
                        month, day, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:
                        return match.group(0)
                except:
                    continue

        # Try month name patterns (September 18, Oct 15, etc.)
        month_patterns = [
            r'(January|Jan)\s+(\d{1,2})',
            r'(February|Feb)\s+(\d{1,2})',
            r'(March|Mar)\s+(\d{1,2})',
            r'(April|Apr)\s+(\d{1,2})',
            r'(May)\s+(\d{1,2})',
            r'(June|Jun)\s+(\d{1,2})',
            r'(July|Jul)\s+(\d{1,2})',
            r'(August|Aug)\s+(\d{1,2})',
            r'(September|Sep)\s+(\d{1,2})',
            r'(October|Oct)\s+(\d{1,2})',
            r'(November|Nov)\s+(\d{1,2})',
            r'(December|Dec)\s+(\d{1,2})'
        ]

        month_map = {
            'January': '01', 'Jan': '01',
            'February': '02', 'Feb': '02',
            'March': '03', 'Mar': '03',
            'April': '04', 'Apr': '04',
            'May': '05',
            'June': '06', 'Jun': '06',
            'July': '07', 'Jul': '07',
            'August': '08', 'Aug': '08',
            'September': '09', 'Sep': '09',
            'October': '10', 'Oct': '10',
            'November': '11', 'Nov': '11',
            'December': '12', 'Dec': '12'
        }

        for pattern in month_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                try:
                    month_name = match.group(1)
                    day = match.group(2).zfill(2)
                    month_num = month_map.get(month_name.title(), month_map.get(month_name.upper()))
                    if month_num:
                        # Assume current year (2025) if no year specified
                        return f"2025-{month_num}-{day}"
                except:
                    continue

        return ""

    def print_events(self, events, target_date):
        """Print events in a formatted way"""
        print(f"\\n🗓️  EVENTS FOR {target_date}")
        print("=" * 60)

        if not events:
            print("📭 No events found for this date")
            return

        for i, event in enumerate(events, 1):
            print(f"\\n🎉 EVENT #{i}")
            print(f"   📋 Title: {event.get('title', 'Unknown')}")
            print(f"   📅 Date: {event.get('date', '')}")
            print(f"   ⏰ Time: {event.get('time', 'Time TBD')}")
            print(f"   📍 Location: {event.get('location', 'Pensacola')}")
            print(f"   🏷️  Category: {event.get('category', 'Event')}")

            if event.get('description'):
                desc = event.get('description', '')
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"   📝 Description: {desc}")

            if event.get('link'):
                print(f"   🔗 Details: {event.get('link', '')}")

        print(f"\\n📊 SUMMARY: {len(events)} event(s) found")

    def save_events_json(self, events, filename=None):
        """Save events to JSON file (optional)"""
        if not filename:
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            print(f"💾 Events saved to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to {filename}: {e}")
            return False

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Get Pensacola events for specific dates')
    parser.add_argument('--date',
                       default=datetime.now().strftime('%Y-%m-%d'),
                       help='Date to search (YYYY-MM-DD format, default: today)')
    parser.add_argument('--days', type=int, default=1,
                       help='Number of days to search from start date (default: 1)')
    parser.add_argument('--save',
                       help='Save results to JSON file (optional)')
    parser.add_argument('--quiet', action='store_true',
                       help='Only output JSON, no formatted display')

    args = parser.parse_args()

    scraper = DailyEventsScraper()

    try:
        # Validate date format
        start_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2025-09-18)")
        return

    all_events = []

    # Search for events across the specified date range
    for day_offset in range(args.days):
        search_date = start_date + timedelta(days=day_offset)
        search_date_str = search_date.strftime('%Y-%m-%d')

        events = scraper.get_events_for_date(search_date_str)
        all_events.extend(events)

        if not args.quiet:
            scraper.print_events(events, search_date_str)
            if day_offset < args.days - 1:  # Not the last iteration
                print("\\n" + "="*60)

    # Save to JSON if requested
    if args.save:
        scraper.save_events_json(all_events, args.save)

    # Output JSON for scripting use
    if args.quiet:
        print(json.dumps(all_events, indent=2))

if __name__ == "__main__":
    main()