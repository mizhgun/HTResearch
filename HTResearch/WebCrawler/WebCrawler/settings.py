# Scrapy settings for WebCrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'WebCrawler'

LOG_ENABLED = False

SPIDER_MODULES = ['webcrawler.spiders', 'webcrawler.unittests']
NEWSPIDER_MODULE = 'webcrawler.spiders'

ITEM_PIPELINES = {
    'htresearch.webcrawler.webcrawler.item_pipeline.item_switches.ItemSwitch' : 100,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'WebCrawler (+http://www.yourdomain.com)'
