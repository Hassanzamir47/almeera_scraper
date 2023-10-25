Almeera Web Scraper

This Python script is designed to scrape data from the 'Almeera' website (https://almeera.online/). It can extract information about categories, subcategories, and products, and save the data in JSON files. The script uses libraries like BeautifulSoup, requests, and joblib for efficient web scraping and data processing.

Features
- Extracts data from the 'Almeera' website.
- Retrieves information about categories, subcategories, and products.
- Downloads and stores images associated with categories and products.
- Parallel processing for faster data extraction.

Requirements
Before running the script, make sure you have the following Python libraries installed:

- BeautifulSoup
- requests
- joblib
- tqdm

You can install these libraries using pip:
pip install beautifulsoup4 requests joblib tqdm

Usage
- Clone or download this repository to your local machine.
- Open the script in a Python environment that meets the requirements mentioned above.
- Customize the main_page_url, output_jsons_path, and output_images_path variables according to your needs.

Output
The script will generate JSON files containing structured data for each category, subcategory, and their associated products. Images will also be downloaded and stored in the specified output directory.
