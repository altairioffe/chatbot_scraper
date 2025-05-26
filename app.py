import streamlit as st
import json
import tempfile
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.roomvo_sitemap import GenericSitemapSpider
from twisted.internet import reactor, defer
from scrapy import signals
from scrapy.signalmanager import dispatcher

# Function to run the spider and collect results
def run_spider(domain):
    results = []

    # Define a custom spider class that collects items
    class CollectingSpider(GenericSitemapSpider):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def parse(self, response):
            for item in super().parse(response):
                results.append(item)
                yield item

    # Clear any previous signals to avoid conflicts
    # dispatcher.disconnectAll()  # Removed due to pydispatcher error

    # Setup crawler process with project settings
    process = CrawlerProcess(get_project_settings())

    # Run the spider
    process.crawl(CollectingSpider, domain=domain)
    process.start()  # the script will block here until the crawling is finished

    return results

def main():
    st.title("Sitemap Scraper")

    domain = st.text_input("Enter the domain to scrape (e.g. example.com):")

    if st.button("Run Scraper"):
        if not domain:
            st.error("Please enter a domain.")
            return

        with st.spinner("Running scraper..."):
            try:
                data = run_spider(domain)
                if not data:
                    st.warning("No data scraped.")
                    return

                # Convert data to JSON string
                json_data = json.dumps(data, indent=2)

                # Create a temporary file for download
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
                    tmp_file.write(json_data.encode('utf-8'))
                    tmp_file_path = tmp_file.name

                # Provide download button
                with open(tmp_file_path, "rb") as f:
                    st.download_button(
                        label="Download JSON",
                        data=f,
                        file_name=f"{domain}_sitemap_data.json",
                        mime="application/json"
                    )

                # Clean up temp file after download button is rendered
                os.unlink(tmp_file_path)

            except Exception as e:
                st.error(f"Error running scraper: {e}")

if __name__ == "__main__":
    main()
