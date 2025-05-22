import scrapy
import re

class RoomvoSpider(scrapy.Spider):
    name = "roomvo"
    
    def __init__(self, domain=None, *args, **kwargs):
        super(RoomvoSpider, self).__init__(*args, **kwargs)
        if domain:
            domain = domain.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "")
            self.allowed_domains = [domain]
            self.start_urls = [f"https://{domain}"]
        else:
            raise ValueError("You must provide a domain argument, e.g. -a domain=example.com")

    def parse(self, response):
        # Clean main content: join all <p> text, collapse whitespace, remove blank lines
        raw_content = " ".join(response.xpath('//p//text()').getall())
        cleaned_content = re.sub(r'\s+', ' ', raw_content).strip()

        yield {
            "page_url": response.url,
            "page_title": response.xpath('//title/text()').get(),
            "main_headings": [h.strip() for h in response.xpath('//h1/text() | //h2/text()').getall() if h.strip()],
            "main_content": cleaned_content,
        }

        # Follow all internal links
        for href in response.xpath('//a[@href]/@href').getall():
            if href.startswith('/'):
                url = response.urljoin(href)
            elif href.startswith('http') and (self.allowed_domains[0] in href):
                url = href
            else:
                continue
            yield scrapy.Request(url, callback=self.parse)
