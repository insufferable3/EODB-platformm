import requests
from bs4 import BeautifulSoup
import json

# 1. Target URL
url = "https://www.startupindia.gov.in/content/sih/en/government-schemes.html"

# List jismein saari scraped schemes store hongi
all_schemes_data = []

try:
    # 2. Website se HTML content fetch karo
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    response.raise_for_status() # Check for HTTP errors (like 404, 500)
    print("URL fetched successfully.")
    
    # 3. BeautifulSoup se HTML parse karo
    soup = BeautifulSoup(response.content, 'html.parser')
    print("HTML parsed.")

    # Selectors based on your screenshots:

    # Main container for all accordion items (Ministries)
    # This might be a div with class 'cmp-accordion' or a parent of all accordion items
    # Looking at image_4aeb49.jpg, the main container seems to be a general div holding cmp-schemes-listing
    # Let's target the individual accordion items which are clearer in image_4aeb86.jpg
    
    # Find all ministry accordion items
    # This div contains both the header (ministry name) and the body (schemes)
    ministry_sections = soup.find_all('div', class_='cmp-accordion__item')
    print(f"Found {len(ministry_sections)} potential ministry sections.")

    if not ministry_sections:
        print("Error: No ministry accordion items found. Please re-verify the class 'cmp-accordion__item'.")
    else:
        for ministry_section in ministry_sections:
            current_ministry = "N/A"
            
            # Find the ministry name (from image_4aeb86.jpg: <a> tag inside cmp-accordion__item-header)
            ministry_name_tag = ministry_section.find('a', class_='cmp-accordion__header-link')
            if ministry_name_tag:
                current_ministry = ministry_name_tag.get_text(strip=True)
            
            print(f"\n--- Processing Ministry: {current_ministry} ---")

            # Find the body of the accordion item where schemes are listed
            # From image_4aeb49.jpg, it's a div with class 'cmp-accordion__item-body'
            accordion_body = ministry_section.find('div', class_='cmp-accordion__item-body')
            
            if accordion_body:
                # Inside the accordion body, find the div that contains the actual scheme listings
                # From image_4aeb49.jpg, it's cmp-schemes-listing__items, inside cmp-schemes-listing
                schemes_listing_container = accordion_body.find('div', class_='cmp-schemes-listing__items')

                if schemes_listing_container:
                    # Now find all individual scheme cards within this container
                    # From image_4aeb80.jpg, each scheme is a div with class 'card scheme-card'
                    scheme_cards = schemes_listing_container.find_all('div', class_='card scheme-card')
                    
                    if not scheme_cards:
                        print(f"  No 'card scheme-card' found within '{current_ministry}'. Skipping.")
                    else:
                        print(f"  Found {len(scheme_cards)} schemes in this ministry.")
                        for card in scheme_cards:
                            # Extract details from each scheme card (from image_4aeb80.jpg)
                            scheme_name_tag = card.find('h5', class_='card-title')
                            scheme_desc_tag = card.find('p', class_='card-text')
                            scheme_link_tag = card.find('a', class_='btn btn-primary') 

                            scheme_name = scheme_name_tag.get_text(strip=True) if scheme_name_tag else "N/A"
                            scheme_description = scheme_desc_tag.get_text(strip=True) if scheme_desc_tag else "N/A"
                            scheme_link = scheme_link_tag['href'] if scheme_link_tag and 'href' in scheme_link_tag.attrs else "N/A"
                            
                            # Make sure the link is absolute (relative URLs ko poora URL banao)
                            if scheme_link and scheme_link.startswith('/'):
                                scheme_link = "https://www.startupindia.gov.in" + scheme_link

                            all_schemes_data.append({
                                "ministry": current_ministry,
                                "name": scheme_name,
                                "description": scheme_description,
                                "link": scheme_link
                            })
                else:
                    print(f"  'cmp-schemes-listing__items' container not found for '{current_ministry}'. Skipping.")
            else:
                print(f"  Accordion body not found for '{current_ministry}'. Skipping.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}. Check your internet connection or URL.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# 4. Scraped data ko JSON file mein save karo
if all_schemes_data:
    with open('government_schemes.json', 'w', encoding='utf-8') as f:
        json.dump(all_schemes_data, f, ensure_ascii=False, indent=4)
    print(f"\nSuccessfully scraped {len(all_schemes_data)} schemes and saved to government_schemes.json")
else:
    print("\nNo schemes were scraped. Check for errors above or HTML selectors.")