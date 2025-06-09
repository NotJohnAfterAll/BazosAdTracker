"""
BazosScraper - A utility for scraping ads from Bazos.cz
This module provides functionality to search for and extract ad information
from the Bazos.cz classified ads website.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

class BazosScraper:
    """
    BazosScraper class for searching and extracting ad information from Bazos.cz
    """
    
    def __init__(self, test_mode=False, ads_to_exclude=None):
        """Initialize the scraper with necessary configuration
        
        Args:
            test_mode: Whether to run in test mode (simulates ad removal)
            ads_to_exclude: List of ad IDs to exclude from results in test mode
        """
        self.base_url = "https://bazos.cz"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'cs,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.seen_ads = set()
        self.logger = logging.getLogger(__name__)
        self.test_mode = test_mode
        self.ads_to_exclude = ads_to_exclude or []

    def search(self, keyword: str, max_pages: int = 5) -> List[Dict]:
        """
        Wrapper method for compatibility with app.py
        
        Args:
            keyword: Search term to look for
            max_pages: Maximum number of pages to search (increased to 5 to find more ads)
            
        Returns:
            List of dictionaries containing ad information
        """
        return self.search_ads(keyword, max_pages)

    def search_ads(self, keyword: str, max_pages: int = 5) -> List[Dict]:
        """
        Search for ads matching a specific keyword across multiple pages
        
        Args:
            keyword: Search term to look for
            max_pages: Maximum number of pages to search
            
        Returns:
            List of dictionaries containing ad information
        """
        ads = []
        
        # Clear seen ads to allow fresh search every time
        # This prevents false "already seen" behavior
        self.seen_ads.clear()
        
        for page in range(max_pages):
            page_ads = self._scrape_page(keyword, page)
            if not page_ads:
                self.logger.info(f"No more ads found for '{keyword}' on page {page + 1}")
                break
                
            ads.extend(page_ads)
            self.logger.info(f"Found {len(page_ads)} ads on page {page + 1} for keyword '{keyword}'")
              # Small delay between pages to avoid rate limiting
            if page < max_pages - 1:
                time.sleep(0.5)
        
        # Apply test mode filtering if enabled
        if self.test_mode and self.ads_to_exclude:
            original_count = len(ads)
            ads = [ad for ad in ads if ad.get('id') not in self.ads_to_exclude]
            filtered_count = original_count - len(ads)
            if filtered_count > 0:
                self.logger.info(f"Test mode: Filtered out {filtered_count} ads for keyword '{keyword}'")
                
        return ads

    def _scrape_page(self, keyword: str, page: int) -> List[Dict]:
        """
        Scrape a single search results page
        
        Args:
            keyword: Search term
            page: Page number (0-based)
            
        Returns:
            List of ad data dictionaries for the page
        """
        try:
            # Construct search URL using the correct format that works with Bazos.cz
            # Bazos uses 'crz' parameter for pagination: crz=0 (page 1), crz=20 (page 2), crz=40 (page 3), etc.
            crz_value = page * 20  # page is 0-based, so page 0 -> crz=0, page 1 -> crz=20, etc.
            url = f"{self.base_url}/search.php?hledat={keyword}&hlokalita=&humkreis=25&cenaod=&cenado=&order=&crz={crz_value}&rz=0"
            
            self.logger.debug(f"Requesting URL: {url}")
            response = self._make_request(url)
            
            if not response:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find ad containers - Bazos uses divs with 'inzeraty inzeratyflex' classes for individual ads
            ad_containers = soup.find_all('div', class_=lambda x: x and 'inzeraty' in x and 'inzeratyflex' in x)
            
            # Filter out the header container (first one usually contains pagination info)
            # and keep only containers that have actual ad links
            actual_ad_containers = []
            for container in ad_containers:
                # Check if this container has a real ad link (to /inzerat/ pages)
                ad_link = container.find('a', href=lambda href: href and '/inzerat/' in href and '.php' in href)
                if ad_link:
                    actual_ad_containers.append(container)
            
            self.logger.debug(f"Found {len(actual_ad_containers)} ad containers on page {page + 1}")
                
            ads = []
            for container in actual_ad_containers:
                ad_data = self._extract_ad_data(container)
                if ad_data and self._is_new_ad(ad_data):
                    ads.append(ad_data)
                    
            return ads
            
        except Exception as e:
            self.logger.error(f"Error scraping page {page + 1} for keyword '{keyword}': {str(e)}")
            return []

    def _extract_ad_data(self, container) -> Optional[Dict]:
        """
        Extract ad data from a container element on the search results page
        
        Args:
            container: BeautifulSoup element containing a single ad listing
            
        Returns:
            Dict containing ad details or None if extraction failed
        """
        try:
            # Find the main ad link - Bazos puts the ad link in h2.nadpis > a
            title_link = container.find('h2', class_='nadpis')
            if title_link:
                title_link = title_link.find('a')
            
            # Fallback: look for any ad link in the container
            if not title_link:
                title_link = container.find('a', href=lambda href: href and '/inzerat/' in href and '.php' in href)
                
            if not title_link:
                self.logger.debug("No title link found in ad container")
                return None
                
            title = title_link.get_text(strip=True)
            href = title_link.get('href', '')
            
            # Construct proper URL
            if href.startswith('http'):
                # Already absolute URL
                url = href
            elif href.startswith('/'):
                # Relative URL starting with /
                url = self.base_url + href
            else:
                # Relative URL not starting with /
                url = f"{self.base_url}/{href}"
            
            # Extract ad ID from URL or href
            ad_id = self._extract_ad_id(href)
            
            # Extract price - Bazos puts price in div.inzeratycena or spans with price info
            price = "N/A"
            price_candidates = [
                container.find('div', class_='inzeratycena'),
                container.find('span', class_=lambda x: x and 'cena' in str(x).lower()),
                container.find(['span', 'div', 'b'], string=lambda x: x and isinstance(x, str) and any(c in x for c in ['Kč', 'CZK', ',-', 'Dohodou']))
            ]
            
            for price_elem in price_candidates:
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text and len(price_text) < 50:  # Reasonable price length
                        price = price_text
                        break
              # Extract date added - Bazos shows date in span with class 'velikost10'
            date_added = "N/A"
            date_elem = container.find('span', class_='velikost10')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Extract date from format like "-TOP- [8.6. 2025]" or similar
                import re
                date_match = re.search(r'\[([^\]]+)\]', date_text)
                if date_match:
                    date_added = date_match.group(1).strip()
                elif date_text:
                    # If no brackets found, try to extract date pattern directly
                    date_pattern_match = re.search(r'\d{1,2}\.\d{1,2}\.?\s*\d{4}?', date_text)
                    if date_pattern_match:
                        date_added = date_pattern_match.group(0).strip()
            
            # Extract description - Bazos puts description in div.popis
            description = title  # Default to title
            description_elem = container.find('div', class_='popis')
            if description_elem:
                desc_text = description_elem.get_text(strip=True)
                if desc_text and len(desc_text) > len(title):
                    description = desc_text
            
            # Extract image URL - usually in the first link's img tag
            image_url = ""
            img_elem = container.find('img', class_='obrazek')
            if not img_elem:
                img_elem = container.find('img')
            
            if img_elem and img_elem.get('src'):
                image_url = img_elem.get('src', '')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
              # Add current date in ISO format for better sorting and display
            current_time = time.time()
            iso_date = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'id': ad_id,
                'title': title,
                'link': url,
                'price': price,
                'date_added': date_added,
                'description': description,
                'image_url': image_url,
                'scraped_at': current_time,
                'date': iso_date
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting ad data: {str(e)}")
            return None

    def _extract_ad_id(self, href: str) -> str:
        """
        Extract ad ID from href
        
        Args:
            href: URL or path containing the ad ID
            
        Returns:
            Ad ID as string
        """
        try:
            # Try to find numeric ID in the href
            match = re.search(r'(\d+)', href)
            if match:
                return match.group(1)
        except Exception:
            pass
            
        try:
            # If no numeric ID found, try to extract from path
            parts = href.strip('/').split('/')
            for part in reversed(parts):
                if part and part.isdigit():
                    return part
        except Exception:
            pass
            
        try:
            # Last resort: generate ID from href
            return str(abs(hash(href)))
        except Exception:
            # Fallback
            return str(int(time.time() * 1000))

    def _make_request(self, url: str, params=None) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling
        
        Args:
            url: URL to request
            params: Optional query parameters
            
        Returns:
            Response object or None if request failed
        """
        try:
            if params:
                response = self.session.get(url, params=params, timeout=10)
            else:
                response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for URL {url}: {str(e)}")
            return None

    def _is_new_ad(self, ad_data: Dict) -> bool:
        """
        Check if ad is new (not seen before)
        
        Args:
            ad_data: Ad data dictionary
            
        Returns:
            True if ad is new, False if already seen
        """
        ad_id = ad_data.get('id')
        if ad_id in self.seen_ads:
            return False
        self.seen_ads.add(ad_id)
        return True

    def clear_seen_ads(self) -> None:
        """Clear the set of seen ads"""
        self.seen_ads.clear()
        self.logger.info("Cleared seen ads cache")

    def get_stats(self) -> Dict:
        """
        Get scraper statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'seen_ads_count': len(self.seen_ads),
            'session_active': bool(self.session)
        }

    def get_ad_details(self, ad_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific ad
        
        Args:
            ad_url: URL of the ad detail page
            
        Returns:
            Dictionary with detailed ad information or None if request failed
        """
        try:
            self.logger.debug(f"Fetching ad details from: {ad_url}")
            response = self._make_request(ad_url)
            
            if not response:
                return None
                
            return self._parse_ad_details(response.text)
            
        except Exception as e:
            self.logger.error(f"Error fetching ad details from {ad_url}: {str(e)}")
            return None

    def _parse_ad_details(self, html_content: str) -> Dict:
        """
        Parse detailed ad page to extract more information
        
        Args:
            html_content: HTML content of the ad detail page
            
        Returns:
            Dictionary with detailed ad information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_element = soup.select_one('h1.nadpisdetail') or soup.find('h1')
            title = title_element.get_text(strip=True) if title_element else "No title"
            
            # Extract price
            price = "Price not listed"
            price_candidates = [
                soup.select_one('.listadvlevo:has(.cenatxt) b'),
                soup.find('b', string=lambda x: x and isinstance(x, str) and ('Kč' in x or 'CZK' in x)),
                soup.find('span', class_=lambda x: x and 'cena' in str(x).lower()),
                soup.find('div', class_=lambda x: x and 'price' in str(x).lower())
            ]
            for price_elem in price_candidates:
                if price_elem:
                    price = price_elem.get_text(strip=True)
                    break
            
            # Extract description
            description = ""
            description_candidates = [
                soup.select_one('#popisdetail'), 
                soup.find('div', {'class': 'popisdetail'}),
                soup.find('div', class_=lambda x: x and 'popis' in str(x).lower()),
                soup.find('div', id=lambda x: x and 'popis' in str(x).lower())
            ]
            for desc_elem in description_candidates:
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            # Extract seller contact info
            seller_name = "Unknown"
            phone = "Not provided"
            email = "Not provided"
            
            # Try multiple approaches for seller name
            seller_candidates = [
                soup.select_one('.listadvdet b'),
                soup.find('b', string=lambda x: not x or not any(word in str(x).lower() for word in ['cena', 'price', 'kč'])),
                soup.find('div', string=lambda text: text and '@' in str(text))
            ]
            for seller_elem in seller_candidates:
                if seller_elem:
                    seller_text = seller_elem.get_text(strip=True)
                    if seller_text and len(seller_text) < 100:  # Avoid picking up long text
                        seller_name = seller_text
                        break
            
            # Look for contact information
            contact_elements = soup.select('.listadvdet') or soup.find_all('div')
            for element in contact_elements:
                text = element.get_text().lower()
                if 'telefon' in text:
                    phone = element.get_text().replace('Telefon:', '').strip()
                elif 'email' in text or 'e-mail' in text:
                    email = element.get_text().replace('Email:', '').replace('E-mail:', '').strip()
            
            # Extract main image
            image_url = ""
            img_candidates = [
                soup.select_one('.carousel-inner .item img'),
                soup.select_one('.fotoobal img'),
                soup.find('img', class_=lambda x: x and any(c in str(x).lower() for c in ['main', 'detail', 'photo'])),
                soup.find('img')
            ]
            for img_element in img_candidates:
                if img_element and img_element.get('src'):
                    image_url = img_element['src']
                    if image_url and not image_url.startswith('http'):
                        image_url = urljoin(self.base_url, image_url)
                    break
            
            return {
                'title': title,
                'price': price,
                'description': description,
                'seller_name': seller_name,
                'phone': phone,
                'email': email,
                'image_url': image_url
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing ad details: {str(e)}")
            return {
                'title': "Error parsing details",
                'price': "N/A",
                'description': "Could not parse ad details",
                'seller_name': "Unknown",
                'phone': "N/A",
                'email': "N/A",
                'image_url': ""
            }
