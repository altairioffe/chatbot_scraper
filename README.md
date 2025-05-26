# Roomvo Sitemap Scraper Streamlit App

This project contains a Streamlit app that allows users to scrape website data from a specified domain's sitemap using a Scrapy spider.

## Using the App

- Enter the domain you want to scrape (e.g., `example.com`).
- Click the "Run Scraper" button.
- Wait for the scraper to finish.
- Download the scraped data as a JSON file using the provided download button.

## Notes

- The scraper dynamically targets the sitemap at `https://<domain>/sitemap.xml`.
- The app runs the scraper programmatically and provides the output as a downloadable JSON file.
