import requests
import bs4
import re
from time import sleep
import random

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from urllib.parse import urlparse, unquote


class MySpider(scrapy.Spider):
    name = "my_spider"
    
    custom_settings = {
        'FEEDS': {
            'data/temp.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'overwrite': True
            }
        },
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        # 'DOWNLOAD_DELAY': 0.2,
        'LOG_LEVEL': 'INFO'
    }

    def assign_source(self):
        print("Assigning source type...")
        self.source_type = 'wiki'
        if self.user_source_type is not None:
            self.source_type = self.user_source_type
        else:
            if 'wikipedia.org' in self.start_url:
                self.source_type = 'wiki'
            elif 'fandom.com' in self.start_url:
                self.source_type = 'fandom'
            
        print("Setting source type to", self.source_type)

    def __init__(self, 
                 max_links = 1000, 
                 start_url = 'https://en.wikipedia.org/wiki/Monkey',
                 allow_random = True,
                 user_source_type = None,
                 min_word_count = 50,
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.links_to_visit = [start_url]
        self.max_links = int(max_links)
        self.max_to_visit = self.max_links * 10
        self.visited = set()
        self.saved_urls = 0
        self.stopped = 0
        self.allow_random = allow_random
        self.min_word_count = min_word_count  # minimum word count in text to be saved
        self.user_source_type = user_source_type
        self.start_url = start_url
        self.assign_source()
   
    def is_article(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        
        invalid_prefixes = (
            '/wiki/wikipedia:',
            '/wiki/help:',
            '/wiki/talk:',
            '/wiki/file:',
            '/wiki/category:',
            '/wiki/template:',
            '/wiki/portal:',
            '/wiki/special:',
            '/wiki/draft:',
            '/wiki/module:',
            '/wiki/user:',
            '/wiki/forum:',
            '/wiki/message_wall:',
            'wiki/Template_talk'
        )

        path = parsed.path.lower()
        if path.startswith(invalid_prefixes):
            return False

        return any(d in parsed.netloc for d in ('en.wikipedia.org', 'fandom.com'))

    def parse(self, response):
        if self.saved_urls % 100 == 0:
            print(f"Saved URLs: {self.saved_urls}")
            print(f"Scheduled URLs: {len(self.links_to_visit)}")
            print(f"Stopped URLs (too short): {self.stopped}")

        # If we've already reached the target, stop immediately
        if self.saved_urls >= self.max_links:
            raise CloseSpider('collected-enough')

        # Remove this URL from scheduled queue (if present) because we're visiting it now
        try:
            self.links_to_visit.remove(response.url)
        except ValueError:
            pass

        # Process and yield item for this page if it's a desired article
        if response.url not in self.visited and self.is_article(response.url):
            self.visited.add(response.url)
            # --- extract title ---
            title = response.css('span.mw-page-title-main::text').get()  # Wikipedia-style title
            if not title:
                title = response.css('h1::text').get() or response.css('title::text').get()
            title = re.sub(r'\s+', ' ', title).strip()
            if not title:
                title = "Untitled page"

            # --- extract text ---
            page_text = ' '.join(response.css('p::text').getall())
            page_text = re.sub(r'[^\w\s]', ' ', page_text, flags=re.UNICODE)
            page_text = re.sub(r'\s+', ' ', page_text).strip()

            # don't yield very short texts
            word_count = len(page_text.split())
            if word_count < self.min_word_count:
                self.stopped += 1
            else:
                yield {
                    'url': response.url, 
                    'title': title, 
                    'text': page_text
                }
                self.saved_urls += 1

        for link in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(link)
            if (len(self.links_to_visit) < self.max_to_visit) and absolute_url not in self.visited and absolute_url not in self.links_to_visit and self.is_article(absolute_url):
                self.links_to_visit.append(absolute_url)

        # --- pick 5 random links from the current stack to yield ---
        # allows for more diverse set of articles
        num_to_yield = min(5, len(self.links_to_visit))

        for _ in range(num_to_yield):
            next_url = self.links_to_visit.pop(random.randrange(len(self.links_to_visit)))
            yield scrapy.Request(next_url, callback=self.parse)

        # rather not usefull unless we got an incorrect starting point
        if self.allow_random and len(self.links_to_visit) == 0 and self.saved_urls + len(self.links_to_visit) < self.max_links:
            random_url = None
            if self.source_type == 'wiki':
                random_url = "https://en.wikipedia.org/wiki/Special:Random"
            elif self.source_type == 'fandom':
                random_url = "https://community.fandom.com/wiki/Special:Random"
            print(f"No new links found, fetching random article: {random_url}")
            yield scrapy.Request(random_url, callback=self.parse)

# run the spider
# scrapy runspider my_spider.py 
# additional parameters:
# -a max_links # maximum number of links to collect
# -a start_url # starting URL
# -a min_word_count # minimum word count in text to be saved
# -a allow_random # whether to fetch random articles when stuck
# -a source_type # 'wiki' or 'fandom' to restrict to one source
