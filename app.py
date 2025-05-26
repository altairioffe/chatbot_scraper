import streamlit as st
import json
import tempfile
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.generic_sitemap import GenericSitemapSpider
import sys

# Install AsyncioSelectorReactor as early as possible before any other Twisted imports
if not hasattr(sys, "is_asyncio_reactor_installed"):
    from twisted.internet import asyncioreactor
    try:
        asyncioreactor.install()
        sys.is_asyncio_reactor_installed = True
    except Exception:
        pass

from twisted.internet import reactor, defer
from scrapy import signals
from scrapy.signalmanager import dispatcher

import multiprocessing
import json

def run_spider_process(domain, queue):
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from spiders.generic_sitemap import GenericSitemapSpider

    results = []

    class CollectingSpider(GenericSitemapSpider):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def parse(self, response):
            for item in super().parse(response):
                print(f"DEBUG: Yielding item: {item}")
                results.append(item)
                yield item

    process = CrawlerProcess(get_project_settings())
    process.crawl(CollectingSpider, domain=domain)
    process.start()

    queue.put(results)

def run_spider(domain):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_spider_process, args=(domain, queue))
    p.start()
    p.join()
    results = []
    while not queue.empty():
        batch = queue.get()
        print(f"DEBUG: Retrieved batch of {len(batch)} items from queue")
        results.extend(batch)
    print(f"DEBUG: Total results collected: {len(results)}")
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
