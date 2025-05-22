import sys
import subprocess

def run_spider(domain):
    cmd = [
        sys.executable, "-m", "scrapy", "crawl", "generic_sitemap",
        "-a", f"domain={domain}",
        "-o", "output.json"
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_spider_colab.py <domain>")
        sys.exit(1)
    domain = sys.argv[1]
    run_spider(domain)
