#!/usr/bin/env python3
"""
Script to scrape district court website information from the U.S. Courts website.
Outputs a CSV file with court names, abbreviations, and URLs.
"""

import logging
import os
from typing import Dict, List, Optional
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SOURCE_URL = "https://www.uscourts.gov/about-federal-courts/court-role-and-structure/court-website-links"
OUTPUT_DIR = "scripts/output"
OUTPUT_FILE = "district_courts.csv"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)


class CourtScraper:
    """Class to handle scraping and processing of court website data."""

    def __init__(self):
        """Initialize the scraper with necessary attributes."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def fetch_page(self) -> Optional[str]:
        """Fetch the webpage content."""
        try:
            response = self.session.get(SOURCE_URL)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching webpage: {e}")
            return None

    def extract_court_data(self, html_content: str) -> List[Dict[str, str]]:
        """Extract court data from HTML content."""
        soup = BeautifulSoup(html_content, "lxml")
        courts_data = []

        # Find the table with class="usa-table"
        table = soup.find("table", class_="usa-table")
        if not table:
            logger.error("Could not find the target table")
            return courts_data

        # Process each row in the table
        for row in table.find_all("tr"):
            # Get all cells in the row
            cells = row.find_all("td")

            # Skip header row and empty rows
            if not cells:
                continue

            # Only process the first column
            first_cell = cells[0]
            links = first_cell.find_all("a")

            for link in links:
                url = link.get("href", "").strip()
                court_name = link.text.strip()

                # Skip empty or non-court links
                if not url or not court_name or "uscourts.gov" not in url:
                    continue

                # Extract abbreviation from URL
                abbreviation = self._extract_abbreviation(url)

                if abbreviation and court_name:
                    # Only add if it's a district court (ends with 'd')
                    if abbreviation.endswith("d"):
                        courts_data.append(
                            {
                                "court": court_name,
                                "abbreviation": abbreviation,
                                "url": url,
                            }
                        )
                        logger.debug(f"Found district court: {court_name}")

        logger.info(f"Found {len(courts_data)} district courts")
        return courts_data

    def _extract_abbreviation(self, url: str) -> Optional[str]:
        """Extract court abbreviation from URL."""
        try:
            # Parse the URL and get the subdomain
            parsed_url = urlparse(url)
            subdomain = parsed_url.netloc.split(".")[0]

            # Remove 'www' if present
            if subdomain == "www":
                subdomain = parsed_url.netloc.split(".")[1]

            return subdomain
        except Exception as e:
            logger.error(f"Error extracting abbreviation from URL {url}: {e}")
            return None

    def save_to_csv(self, data: List[Dict[str, str]]) -> bool:
        """Save the court data to a CSV file."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # Create DataFrame and save to CSV
            df = pd.DataFrame(data)
            df.to_csv(OUTPUT_PATH, index=False)
            logger.info(f"Successfully saved data to {OUTPUT_PATH}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            return False

    def validate_data(self, data: List[Dict[str, str]]) -> bool:
        """Validate the extracted data."""
        if not data:
            logger.error("No data was extracted")
            return False

        # Check for required columns
        required_columns = {"court", "abbreviation", "url"}
        for item in data:
            if not all(col in item for col in required_columns):
                logger.error("Missing required columns in data")
                return False

        # Check for duplicate entries
        courts = [item["court"] for item in data]
        if len(courts) != len(set(courts)):
            logger.warning("Duplicate court entries found")

        return True


def main():
    """Main function to orchestrate the scraping process."""
    scraper = CourtScraper()

    # Fetch webpage content
    html_content = scraper.fetch_page()
    if not html_content:
        return

    # Extract court data
    courts_data = scraper.extract_court_data(html_content)

    # Validate data
    if not scraper.validate_data(courts_data):
        return

    # Save to CSV
    scraper.save_to_csv(courts_data)


if __name__ == "__main__":
    main()
