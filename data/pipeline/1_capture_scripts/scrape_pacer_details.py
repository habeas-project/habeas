"""
Scrapes court details (address, phone, email, counties) from PACER lookup URLs.

Reads court abbreviations from an input CSV, scrapes data from the corresponding
PACER court lookup page, updates the input CSV with contact details, and creates
a new CSV mapping courts to the counties they serve.
"""

import argparse
import csv
import re
import time
from pathlib import Path
from typing import List, Optional, TypedDict

import requests
from bs4 import BeautifulSoup, Tag


# Define type hints for clarity
class CourtInputData(TypedDict):
    court: str
    abbreviation: str
    url: str  # Original URL from input, might not be used directly for scraping


# CourtOutputData is being removed as district_courts_updated.csv is deprecated
# class CourtOutputData(TypedDict):
#     court: str
#     abbreviation: str
#     url: str


class CountyOutputData(TypedDict):
    court_abbreviation: str
    county_name: str
    state: str


# New TypedDict for individual contact locations for the new CSV
class CourtContactData(TypedDict):
    court_abbreviation: str
    location_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    hours: Optional[str]


# New TypedDicts for scraper return structure
class ScrapedCourtContactLocation(TypedDict):
    location_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    hours: Optional[str]


class ScrapedCourtPageData(TypedDict):
    counties: List[str]
    state: Optional[str]
    contact_locations: List[ScrapedCourtContactLocation]


# Constants
PACER_LOOKUP_URL_TEMPLATE = (
    "https://pacer.uscourts.gov/file-case/court-cmecf-lookup/court/{abbr}C"
)
DEFAULT_INPUT_CSV = Path("data/pipeline/2_staging_data/uscourts_foundations.csv")
# DEFAULT_OUTPUT_COURTS_CSV is being removed
# DEFAULT_OUTPUT_COURTS_CSV = Path("scripts/output/district_courts_updated.csv")
DEFAULT_OUTPUT_COUNTIES_CSV = Path(
    "data/pipeline/2_staging_data/pacer_court_counties.csv"
)
DEFAULT_OUTPUT_CONTACT_CSV = Path(
    "data/pipeline/2_staging_data/pacer_court_contacts.csv"
)
REQUEST_DELAY_SECONDS = 1  # Delay between requests to avoid overwhelming the server

# Browser-like User-Agent to help avoid being blocked
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def construct_pacer_url(abbreviation: str) -> str:
    """Constructs the PACER CM/ECF lookup URL for a given court abbreviation."""
    # Ensure abbreviation is uppercase before the check
    processed_abbreviation = abbreviation.upper()
    if processed_abbreviation == "ID":
        processed_abbreviation = "IDDC"
    return PACER_LOOKUP_URL_TEMPLATE.format(abbr=processed_abbreviation)


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean up extracted text by removing extra whitespace and newlines."""
    if text is None:
        return None
    # Remove extra whitespace, tabs, and newlines
    cleaned = " ".join(text.strip().split())
    return cleaned if cleaned else None


def extract_state_from_address(address: Optional[str]) -> Optional[str]:
    """Try to extract the state from an address string."""
    if not address:
        return None

    # Look for state abbreviation in the last part of the address (ZIP code line)
    # State abbreviations are typically 2 uppercase letters followed by a space and ZIP code
    parts = address.split(",")
    if len(parts) < 2:
        return None

    # Last part might contain state and ZIP like "CA 94102"
    last_part = parts[-1].strip()
    # Try to find a pattern of 2 uppercase letters followed by a space and digits
    match = re.search(r"([A-Z]{2})\s+\d", last_part)
    if match:
        return match.group(1)

    return None


def scrape_court_details(abbreviation: str) -> ScrapedCourtPageData:
    """
    Scrapes the PACER lookup page for a given court abbreviation.

    Args:
        abbreviation: The court abbreviation (e.g., 'cand').

    Returns:
        A dictionary containing scraped data:
        {
            "counties": ["County A", "County B"],
            "state": "CA",
            "contact_locations": [
                {"location_name": "Main Office", "address": "...", ...},
                ...
            ]
        }
    """
    url = construct_pacer_url(abbreviation.upper())
    print(f"Scraping {url}")

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {
            "counties": [],
            "state": None,
            "contact_locations": [],
        }

    soup = BeautifulSoup(response.text, "html.parser")

    # Initialize data structure for return
    scraped_page_data: ScrapedCourtPageData = {
        "counties": [],
        "state": None,
        "contact_locations": [],
    }

    # ---- Look for "Counties in this District" section ----
    counties: List[str] = []
    state_from_counties: Optional[str] = None

    counties_heading = None
    for heading in soup.find_all(["h2", "h3", "h4"]):
        if not isinstance(heading, Tag):
            continue
        if "Counties in this District" in heading.text:
            counties_heading = heading
            break

    if counties_heading:
        counties_table = counties_heading.find_next("table")
        if counties_table and isinstance(counties_table, Tag):
            for row in counties_table.find_all("tr"):
                if not isinstance(row, Tag) or not row.find_all("td"):
                    continue
                cells = row.find_all("td")
                if len(cells) >= 2:
                    county_name = clean_text(cells[0].text)
                    if county_name:
                        counties.append(county_name)
                    if not state_from_counties and len(cells) > 1:
                        state_text = clean_text(cells[1].text)
                        if state_text:
                            state_from_counties = state_text

    scraped_page_data["counties"] = counties
    scraped_page_data["state"] = state_from_counties

    # ---- Look for "Court Locations and Contact Information" section ----
    all_contact_locations: List[ScrapedCourtContactLocation] = []
    contact_heading: Optional[Tag] = None
    for heading in soup.find_all(["h2", "h3", "h4"]):
        if not isinstance(heading, Tag):
            continue
        if any(
            term in heading.text for term in ["Court Locations", "Contact Information"]
        ):
            contact_heading = heading
            print(f"Found contact_heading: '{contact_heading.text.strip()}'")
            break

    if not contact_heading:
        print(f"DEBUG: contact_heading was NOT found for {abbreviation}.")

    potential_contact_tables: List[Tag] = []
    if contact_heading:
        # print(f"DEBUG: Iterating siblings for contact_heading for {abbreviation}") # DEBUG
        element_after_heading = contact_heading.find_next_sibling()

        if element_after_heading and isinstance(element_after_heading, Tag):
            # print(f"DEBUG: Element after heading is: {element_after_heading.name}") # DEBUG
            if element_after_heading.name == "div":
                # print(f"DEBUG: Found div after heading, looking for tables within it.") # DEBUG
                tables_in_div = []
                for child_element in element_after_heading.children:
                    if isinstance(child_element, Tag):
                        if child_element.name == "table":
                            tables_in_div.append(child_element)
                        elif child_element.name in ["h2", "h3", "h4"]:
                            break
                potential_contact_tables.extend(tables_in_div)
            elif element_after_heading.name == "table":
                # print(f"DEBUG: Found table directly after heading.") # DEBUG
                potential_contact_tables.append(element_after_heading)
                current_element = element_after_heading.find_next_sibling()
                while current_element:
                    # print(f"DEBUG: Subsequent sibling: {type(current_element)} - Name: {getattr(current_element, 'name', 'N/A')}") # DEBUG
                    if (
                        isinstance(current_element, Tag)
                        and current_element.name == "table"
                    ):
                        potential_contact_tables.append(current_element)
                    elif isinstance(current_element, Tag) and current_element.name in [
                        "h2",
                        "h3",
                        "h4",
                    ]:
                        break
                    current_element = current_element.find_next_sibling()
            elif element_after_heading.name not in ["h2", "h3", "h4"]:
                pass  # print(f"DEBUG: Element after heading is {element_after_heading.name}, not a div/table/heading. Stopping search here for now.")

    else:
        # print(f"DEBUG: contact_heading was NOT found for {abbreviation}.") # DEBUG
        potential_contact_tables = [
            t for t in soup.find_all("table") if isinstance(t, Tag)
        ]
        if counties_heading and counties_table in potential_contact_tables:
            potential_contact_tables.remove(counties_table)

    # print(f"Found {len(potential_contact_tables)} potential contact tables for {abbreviation}.") # DEBUG

    for table_idx, table in enumerate(potential_contact_tables):
        # print(f"Processing table {table_idx + 1} for {abbreviation}") # DEBUG
        current_location: ScrapedCourtContactLocation = {
            "location_name": None,
            "address": None,
            "phone": None,
            "email": None,
            "hours": None,
        }
        rows = table.find_all("tr")
        for row in rows:
            if not isinstance(row, Tag):
                continue
            cells = row.find_all(["th", "td"])
            if len(cells) < 2:
                continue

            header_text = clean_text(cells[0].text.strip().lower())
            value_text = clean_text(cells[1].text.strip())  # General clean

            if not header_text or not value_text:
                # DEBUG: print if row is skipped due to empty header/value
                # print(f"Skipping row in table {table_idx + 1} for {abbreviation} due to empty header/value. Header: '{cells[0].text.strip()}', Value: '{cells[1].text.strip()}'")
                continue

            # DEBUG: print extracted header and value
            # print(f"  Table {table_idx + 1} Row - Header: '{header_text}', Value: '{value_text}'")

            if "name" in header_text:
                current_location["location_name"] = value_text
            elif "address" in header_text:
                address_indicators = [
                    "street",
                    "avenue",
                    "ave",
                    "blvd",
                    "road",
                    "suite",
                    "p.o. box",
                    "box",
                ]
                has_digits = any(c.isdigit() for c in value_text)
                has_address_term = any(
                    term in value_text.lower() for term in address_indicators
                )
                if has_digits or has_address_term:
                    current_location["address"] = value_text
                # Sometimes email is in address field
                elif (
                    "@" in value_text
                    and "." in value_text
                    and not current_location["email"]
                ):
                    current_location["email"] = value_text
            elif any(word in header_text for word in ["phone", "telephone"]):
                if any(c.isdigit() for c in value_text):
                    current_location["phone"] = value_text
            elif "email" in header_text or "e-mail" in header_text:
                if "@" in value_text and "." in value_text:
                    current_location["email"] = value_text
                value_cell = cells[1]
                if isinstance(value_cell, Tag) and not current_location["email"]:
                    # Ensure href is a string before calling startswith
                    email_link = value_cell.find(
                        "a",
                        href=lambda h_attr: isinstance(h_attr, str)
                        and h_attr.startswith("mailto:"),
                    )
                    if email_link and isinstance(email_link, Tag):
                        href_val = email_link.get("href")
                        if isinstance(href_val, str):  # Ensure href_val is a string
                            current_location["email"] = href_val.replace("mailto:", "")
            elif "hours" in header_text:
                current_location["hours"] = value_text

        # Add location if it has some identifiable information
        if any(current_location.values()):
            all_contact_locations.append(current_location)
            # print(f"Added location to all_contact_locations for {abbreviation}: {current_location}") # DEBUG
        # else:
        # print(f"No values found for current_location in table {table_idx + 1} for {abbreviation}, not adding.") # DEBUG

    scraped_page_data["contact_locations"] = all_contact_locations

    # If overall state not found from counties, try to get from first contact address
    if not scraped_page_data["state"] and all_contact_locations:
        first_address_with_state = next(
            (loc["address"] for loc in all_contact_locations if loc["address"]), None
        )
        if first_address_with_state:
            extracted_state = extract_state_from_address(first_address_with_state)
            if extracted_state:
                scraped_page_data["state"] = extracted_state

    # Print what we found for debugging
    print(f"Scraped {len(scraped_page_data['counties'])} counties for {abbreviation}")
    if scraped_page_data["state"]:
        print(f"Overall State: {scraped_page_data['state']}")
    for i, loc in enumerate(scraped_page_data["contact_locations"]):
        print(f"  Location {i + 1}:")
        print(f"    Name: {loc['location_name']}")
        print(f"    Address: {loc['address']}")
        print(f"    Phone: {loc['phone']}")
        print(f"    Email: {loc['email']}")
        print(f"    Hours: {loc['hours']}")

    return scraped_page_data


def read_input_csv(input_path: Path) -> List[CourtInputData]:
    """Reads the input CSV file containing court abbreviations."""
    courts: List[CourtInputData] = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames or not all(
                f in reader.fieldnames for f in ["court", "abbreviation", "url"]
            ):
                raise ValueError(
                    "Input CSV missing required columns: 'court', 'abbreviation', 'url'"
                )
            for row in reader:
                # Basic validation
                if row.get("abbreviation"):
                    courts.append(
                        {
                            "court": row.get("court", ""),
                            "abbreviation": row["abbreviation"],
                            "url": row.get("url", ""),
                        }
                    )
                else:
                    print(f"Skipping row due to missing abbreviation: {row}")

    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        return []
    except Exception as e:
        print(f"ERROR: Failed to read input CSV {input_path}: {e}")
        return []
    return courts


# write_output_courts_csv is being removed as district_courts_updated.csv is deprecated
# def write_output_courts_csv(
#     output_path: Path, court_data: List[CourtOutputData]
# ) -> None:
#     """Writes the updated court data (including scraped details) to a CSV."""
#     if not court_data:
#         print("No court data to write.")
#         return
#
#     fieldnames = ["court", "abbreviation", "url"]
#     try:
#         with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(court_data)
#         print(f"Successfully wrote updated court data to {output_path}")
#     except Exception as e:
#         print(f"ERROR: Failed to write court output CSV to {output_path}: {e}")


def write_output_counties_csv(
    output_path: Path, county_data: List[CountyOutputData]
) -> None:
    """Writes the scraped county data to a new CSV file."""
    if not county_data:
        print("No county data to write.")
        return

    fieldnames = ["court_abbreviation", "county_name", "state"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(county_data)
        print(f"Successfully wrote county data to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write county output CSV to {output_path}: {e}")


# New function to write court contact details
def write_output_contact_csv(
    output_path: Path, contact_data: List[CourtContactData]
) -> None:
    """Writes the scraped court contact details to a CSV file."""
    if not contact_data:
        print("No court contact data to write.")
        return

    fieldnames = [
        "court_abbreviation",
        "location_name",
        "address",
        "phone",
        "email",
        "hours",
    ]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contact_data)
        print(f"Successfully wrote court contact data to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write court contact output CSV to {output_path}: {e}")


def main(
    input_csv_path: Path, output_counties_path: Path, output_contact_path: Path
) -> None:
    """Main function to orchestrate the scraping and writing process."""
    input_courts = read_input_csv(input_csv_path)
    if not input_courts:
        return

    # updated_court_data is removed as district_courts_updated.csv is deprecated
    all_county_data: List[CountyOutputData] = []
    all_court_contact_data: List[CourtContactData] = []

    for court in input_courts:
        print(f"Processing: {court['court']} ({court['abbreviation']})")
        abbreviation = court["abbreviation"]
        scraped_page_data = scrape_court_details(abbreviation)

        # Data for district_courts_updated.csv is no longer prepared

        # Prepare county data
        counties = scraped_page_data.get("counties", [])
        state_for_counties = scraped_page_data.get("state")

        if counties and isinstance(state_for_counties, str):
            for county_name in counties:
                if isinstance(county_name, str):  # ensure county_name is a string
                    county_data_entry: CountyOutputData = {
                        "court_abbreviation": abbreviation,
                        "county_name": county_name,  # clean_text already applied in scraper
                        "state": state_for_counties,  # clean_text already applied in scraper
                    }
                    all_county_data.append(county_data_entry)

        # Prepare contact location data
        contact_locations = scraped_page_data.get("contact_locations", [])
        for loc_data in contact_locations:
            contact_entry: CourtContactData = {
                "court_abbreviation": abbreviation,
                "location_name": loc_data.get(
                    "location_name"
                ),  # clean_text applied in scraper
                "address": loc_data.get("address"),
                "phone": loc_data.get("phone"),
                "email": loc_data.get("email"),
                "hours": loc_data.get("hours"),
            }
            all_court_contact_data.append(contact_entry)

        time.sleep(REQUEST_DELAY_SECONDS)

    if all_county_data:
        write_output_counties_csv(output_counties_path, all_county_data)
    else:
        print("No county data to write.")

    # Write the new contact data
    if all_court_contact_data:
        write_output_contact_csv(output_contact_path, all_court_contact_data)
    else:
        print("No court contact data to write.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape court details and counties from PACER lookup site."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_CSV,
        help=f"Input CSV file with court abbreviations (default: {DEFAULT_INPUT_CSV})",
    )
    parser.add_argument(
        "--output-counties",
        type=Path,
        default=DEFAULT_OUTPUT_COUNTIES_CSV,
        help=f"Output file for county data (default: {DEFAULT_OUTPUT_COUNTIES_CSV})",
    )
    parser.add_argument(
        "--output-contact",
        type=Path,
        default=DEFAULT_OUTPUT_CONTACT_CSV,
        help=f"Output file for court contact details (default: {DEFAULT_OUTPUT_CONTACT_CSV})",
    )
    args = parser.parse_args()

    main(args.input, args.output_counties, args.output_contact)
