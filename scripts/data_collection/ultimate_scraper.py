#!/usr/bin/env python3
"""
Ultimate Pensacola Events Scraper - Extract actual events from listing cards
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        self.all_events = []
        
    def scrape_all_pages(self, base_url):
        """Scrape all paginated pages"""
        logger.info("Starting to scrape all pages...")
        
        # Get pagination URLs
        pagination_urls = self.get_all_pagination_urls(base_url)
        
        # Process each page
        for i, url in enumerate(pagination_urls, 1):
            logger.info(f"Processing page {i} of {len(pagination_urls)}")
            events = self.scrape_single_page(url)
            self.all_events.extend(events)
            
            logger.info(f"Found {len(events)} events on page {i}")
            
            if i < len(pagination_urls):
                time.sleep(2)  # Rate limiting
                
        logger.info(f"Total events collected: {len(self.all_events)}")
        
    def get_all_pagination_urls(self, base_url):
        """Get all pagination URLs for 75-day period"""
        try:
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find pagination links
            pagination_links = []
            
            # Look for pagination container and extract all page links
            pagination_elements = soup.find_all('a', href=re.compile(r'page=\d+'))
            
            for elem in pagination_elements:
                href = elem.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    pagination_links.append(full_url)
                    
            # Add the original URL (page 1)
            if base_url not in pagination_links:
                pagination_links.insert(0, base_url)
                
            # Remove duplicates and sort by page number
            pagination_links = list(set(pagination_links))
            
            def extract_page_number(url):
                match = re.search(r'page=(\d+)', url)
                return int(match.group(1)) if match else 0
                
            pagination_links.sort(key=extract_page_number)
            
            logger.info(f"Found {len(pagination_links)} pages to scrape")
            
            # Log first few pages
            for i, url in enumerate(pagination_links[:5]):
                page_num = extract_page_number(url)
                logger.info(f"Page {page_num or 1}: {url}")
                
            return pagination_links
            
        except Exception as e:
            logger.error(f"Error getting pagination URLs: {e}")
            return [base_url]
            
    def scrape_single_page(self, url):
        """Scrape events from a single page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find event listing cards (based on analysis, these have card--listing class)
            event_cards = soup.find_all('article', class_=['card', 'card--listing'])
            
            events = []
            for card in event_cards:
                # Only process cards that have the listing class (actual events)
                if 'card--listing' in card.get('class', []):
                    event_data = self.extract_event_from_listing_card(card)
                    if event_data:
                        events.append(event_data)
                        
            return events
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return []
            
    def extract_event_from_listing_card(self, card):
        """Extract event data from a listing card"""
        try:
            # Extract the main event link (Link 2 from our analysis)
            main_links = card.find_all('a')
            
            event_link = None
            title = ""
            
            # Find the title link (usually the second link)
            for link in main_links:
                href = link.get('href', '')
                if '/events/' in href and link.get_text(strip=True) and not link.get('class'):
                    event_link = link
                    title = link.get_text(strip=True)
                    break
                    
            if not event_link or not title:
                return None
                
            # Get the full URL
            full_url = urljoin("https://www.visitpensacola.com", event_link.get('href'))
            
            # Extract date from the card text
            card_text = card.get_text()
            date = self.extract_date_from_card_text(card_text)
            
            # Extract location from card text
            location = self.extract_location_from_card_text(card_text)
            
            # Extract image URL
            image_url = self.extract_image_from_card(card)
            
            # Get detailed info from the event page
            detailed_description, detailed_time = self.get_event_page_details(full_url)
            
            return {
                "title": title.strip(),
                "link": full_url,
                "date": date,
                "time": detailed_time,
                "location": location,
                "description": detailed_description or title.strip(),
                "image": image_url,
                "source": "Visit Pensacola"
            }
            
        except Exception as e:
            logger.error(f"Error extracting event from listing card: {e}")
            return None
            
    def extract_date_from_card_text(self, text):
        """Extract date from card text"""
        # Look for patterns like "September 10", "October 15", etc.
        date_patterns = [
            r'(September|October|November)\s+(\d{1,2})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if pattern == date_patterns[0]:  # Month name format
                        month_map = {'September': '09', 'October': '10', 'November': '11'}
                        month = match.group(1)
                        day = match.group(2).zfill(2)
                        return f"2025-{month_map[month]}-{day}"
                    elif pattern == date_patterns[1]:  # MM/DD/YYYY
                        month, day, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    elif pattern == date_patterns[2]:  # YYYY-MM-DD
                        return match.group(1)
                except:
                    continue
                    
        return ""
        
    def extract_location_from_card_text(self, text):
        """Extract location from card text"""
        # Common location patterns in Pensacola events
        location_patterns = [
            r'(Downtown Pensacola)',
            r'(Pensacola Beach)',
            r'(West Pensacola)', 
            r'(Perdido Key)',
            r'(East Hill)',
            r'(\d+[A-Za-z\s]*(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr))'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return ""
        
    def extract_image_from_card(self, card):
        """Extract image URL from card"""
        img_elem = card.find('img')
        if img_elem:
            # Try data-srcset first (lazy loaded images)
            srcset = img_elem.get('data-srcset') or img_elem.get('srcset')
            if srcset:
                # Extract URLs from srcset and get the largest one
                urls = re.findall(r'(https://[^\s]+)', srcset)
                if urls:
                    return urls[-1]  # Last one is usually highest quality
                    
            # Fallback to src
            src = img_elem.get('data-src') or img_elem.get('src')
            if src and not src.startswith('data:'):
                return urljoin("https://www.visitpensacola.com", src)
                
        return ""
        
    def get_event_page_details(self, url):
        """Get additional details from the event page"""
        try:
            time.sleep(0.5)  # Rate limiting
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description
            description = self.extract_description_from_page(soup)
            
            # Extract time information
            event_time = self.extract_time_from_page(soup)
            
            return description, event_time
            
        except Exception as e:
            logger.error(f"Error getting details from {url}: {e}")
            return "", ""
            
    def extract_description_from_page(self, soup):
        """Extract description from event detail page"""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '').strip()
            if desc and len(desc) > 20:
                return desc[:500]
                
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            desc = og_desc.get('content', '').strip()
            if desc and len(desc) > 20:
                return desc[:500]
                
        # Try to find main content paragraphs
        content_selectors = [
            '.entry-content p',
            '.content p',
            'main p',
            '.description p',
            '.event-description'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = elem.get_text(strip=True)
                if desc and len(desc) > 20:
                    return desc[:500]
                    
        return ""
        
    def extract_time_from_page(self, soup):
        """Extract time from event page"""
        text_content = soup.get_text()
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*[APap][Mm](?:\s*-\s*\d{1,2}:\d{2}\s*[APap][Mm])?)',
            r'(\d{1,2}\s*[APap][Mm](?:\s*-\s*\d{1,2}\s*[APap][Mm])?)',
            r'(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_content)
            if match:
                return match.group(1)
                
        return ""
        
    def clean_and_deduplicate(self):
        """Clean and remove duplicates"""
        seen = set()
        cleaned_events = []
        
        for event in self.all_events:
            title = event.get('title', '').strip()
            date = event.get('date', '')
            
            if not title or len(title) < 5:
                continue
                
            # Create deduplication key
            key = (title.lower().strip(), date)
            
            if key not in seen:
                seen.add(key)
                cleaned_events.append(event)
                
        self.all_events = cleaned_events
        logger.info(f"After cleaning: {len(cleaned_events)} unique events")
        
    def save_events(self, filename):
        """Save events to JSON file"""
        self.clean_and_deduplicate()
        
        # Sort by date and title
        self.all_events.sort(key=lambda x: (x.get('date', ''), x.get('title', '')))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_events, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(self.all_events)} events to {filename}")
        return len(self.all_events)
        
    def run(self, base_url):
        """Run the complete scraping process"""
        logger.info("Starting ultimate Pensacola events scraper...")
        
        # Scrape all pages
        self.scrape_all_pages(base_url)
        
        # Save results
        total = self.save_events('../../pensacola_events.json')
        
        logger.info(f"Scraping complete! {total} events saved.")
        return total

if __name__ == "__main__":
    scraper = UltimateEventsScraper()
    
    # Test with 10-day range (until 09/20) - should get 66 events
    base_url = "https://www.visitpensacola.com/events/?range=1&date-from=2025-09-10&date-to=2025-09-20&categories=544740%2C544743%2C544744%2C544746%2C544751%2C544752%2C2581955&regions=&keyword=&calendar=1"
    
    scraper.run(base_url)