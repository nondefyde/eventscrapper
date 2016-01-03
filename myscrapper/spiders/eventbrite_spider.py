import scrapy
from datetime import datetime
from myscrapper.items import EventItem


class EventBriteSpider(scrapy.Spider):
    name = "event"
    allowed_domains = ["eventbrite.com"]

    pagination_max_num = 182
    entry_url = 'https://www.eventbrite.com/d/tx--arlington/events/?crt=regular&page=%s&radius=155.399286739&slat=32.7357&slng=-97.1081&sort=best'

    start_urls = []

    def __init__(self, **kwargs):
        super(EventBriteSpider, self).__init__(**kwargs)

        for page_num in range(1, self.pagination_max_num):
            url = self.entry_url % page_num
            self.start_urls = self.start_urls + [url]

    def parse(self, response):
        # for href in response.css('section.js-content div.g-cell a.js-event-link::attr(href)'):
        for href in response.css('section.js-content div.g-cell'):
            item = EventItem()
            item['category'] = 'null'

            url = href.css('a.js-event-link::attr(href)').extract()[0].strip()
            item['source'] = url

            try:
                category = href.css('div.poster-card__tags a.event-format::text').extract()[0]
                item['category'] = category[1:]
            except Exception as e:
                item['category'] = ''
            pass

            try:
                industry = href.css('div.poster-card__tags a.event-category::text').extract()[0]
                item['industry'] = industry[1:]
            except Exception as e:
                item['industry'] = ''
            pass

            item['event_website'] = 'https://www.eventbrite.com'

            item['price_range'] = href.css('a.js-event-link span.poster-card__label::text').extract()[0]

            request = scrapy.Request(url, callback=self.parse_event, meta={'item': item})
            yield request

    def parse_event(self, response):
        item = response.meta['item']

        sel = response.css('html')

        item['title'] = sel.css('title::text').extract()[0].strip()

        item['description'] = ''
        try:
            item['description'] = sel.css('div.panel_section').extract()[0]
        except Exception as e:
            item['description'] = sel.css('div.js-xd-read-more-contents').extract()[0]
        pass

        date = sel.css('table h2 meta::attr(content)').extract()
        if len(date) == 0:
            date = sel.css('dd.event-detail-data meta::attr(content)').extract()

        item['date'] = date

        item['event_start'] = '0000-00-00 00:00:0'
        item['event_end'] = '0000-00-00 00:00:0'

        if len(date) > 1:
            if len(date[0]) > 18 and date[1] > 18:
                event_start = date[0][0:19]
                event_end = date[1][0:19]

                item['event_start'] = datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                item['event_end'] = datetime.strptime(event_end, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

        item['name'] = ''
        item['postalCode'] = ''
        item['location'] = ''
        item['addressCountry'] = ''
        item['addressRegion'] = ''
        item['addressLocality'] = ''
        item['streetAddress'] = ''

        metas = sel.css('span[itemprop=location] span meta::attr(itemprop)').extract()
        location = sel.css('span[itemprop=location] span meta::attr(content)').extract()

        n = len(location)
        if n > 8:
            n = 8

        for index in range(n):
            item[metas[index]] = location[index]

        item['location'] = item['name']

        yield item
