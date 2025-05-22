import scrapy
from scrapy.spiders import SitemapSpider
import re

class GenericSitemapSpider(SitemapSpider):
    name = "generic_sitemap"
    allowed_domains = []
    sitemap_urls = []

    def __init__(self, domain=None, *args, **kwargs):
        super(GenericSitemapSpider, self).__init__(*args, **kwargs)
        if domain:
            domain = domain.strip().lower()
            self.allowed_domains = [domain.replace("https://", "").replace("http://", "").replace("www.", "")]
            self.sitemap_urls = [f"https://{self.allowed_domains[0]}/sitemap.xml"]
        else:
            raise ValueError("You must provide a domain argument, e.g. -a domain=example.com")

    def parse(self, response):
        url = response.url.strip()
        title = (response.xpath('//title/text()').get() or "").strip()
        headings = [re.sub(r'\s+', ' ', h.strip()) for h in response.xpath('//h1/text() | //h2/text()').getall() if h.strip()]

        # Remove unwanted string and following address sentence from all headings
        def clean_text(text):
            # Remove the fixed unwanted string and everything after it (address, etc.)
            pattern = (r"This site is protected by reCAPTCHA and the Google Privacy Policy and Terms of Service apply\. "
                       r"There was an error submitting your request\. Please try again\. Thank you! We'll be in touch shortly\..*")
            return re.sub(pattern, "", text, flags=re.DOTALL).strip()

        headings = [clean_text(h) for h in headings]

        if "/products/catalog/" in url and headings:
            # Try to extract product_name and brand_name from the first heading
            m = re.match(r"Product Details for (.+) by (.+)", headings[0])
            # Extract product_type and product_category from the URL
            type_cat_match = re.search(r"/products/catalog/([^/]+)/([^/]+)/", url)
            product_type = type_cat_match.group(1) if type_cat_match else ""
            product_category = type_cat_match.group(2) if type_cat_match else ""
            if m:
                product_name = m.group(1).strip()
                brand_name = m.group(2).strip()
                yield {
                    "page_url": url,
                    "product_name": product_name,
                    "brand_name": brand_name,
                    "product_type": product_type,
                    "product_category": product_category,
                }
                return  # Only output this for product pages
        if "/products/catalog" in url:
            # For other catalog pages, only include the first two headings, trimmed
            yield {
                "page_url": url,
                "main_headings": [h for h in headings[:2]],
            }
        else:
            # For all other pages, include main_content as before, with improved whitespace trimming and cleanup
            raw_content = " ".join(response.xpath('//p//text()').getall())
            cleaned_content = re.sub(r'\s+', ' ', raw_content).strip()
            cleaned_content = clean_text(cleaned_content)
            yield {
                "page_url": url,
                "page_title": title,
                "main_headings": headings,
                "main_content": cleaned_content,
            }
