cd HTResearch/WebCrawler

set query=%1
set numPages=%2

echo %query%
echo %numPages%

scrapy crawl publication_spider -a start_url="http://scholar.google.com/scholar?q=%query%&hl=en" & for /l %%x in (1, 1, %numPages%) do (scrapy crawl publication_spider -a start_url="http://scholar.google.com/scholar?start=%%x0&q=%query%&hl=en" & echo "http://scholar.google.com/scholar?start=%%x0&q=%query%&hl=en")