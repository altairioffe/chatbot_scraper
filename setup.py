from setuptools import setup, find_packages

setup(
    name="roomvo_sitemap_scraper",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "scrapy",
        "streamlit",
        "twisted",
    ],
)
