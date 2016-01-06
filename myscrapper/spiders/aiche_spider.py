import scrapy
from datetime import datetime
from datetime import date
from geolocation.main import GoogleMaps
import json
from myscrapper.items import EventItem


class EventEyeSpider(scrapy.Spider):
    google_maps = ''
    month = []

    name = "aiche"
    allowed_domains = ["aiche.org"]
    start_urls = ['http://www.aiche.org/resources/conferences']

    def __init__(self, **kwargs):
        super(EventEyeSpider, self).__init__(**kwargs)
        self.init_Month()
        self.google_maps = GoogleMaps(api_key='AIzaSyCaxLzZ2r7AbCJiIy5RtJ4jOQXcOlDbeV0')

    def parse(self, response):
        titles = response.css('div.view-content div.views-row article h3 a::text').extract()
        urls = response.css('div.view-content div.views-row article h3 a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = EventItem()
            complete_url = url
            item['url'] = 'http://www.aiche.org' + complete_url
            item['title'] = titles[num]
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request
            # break

    def parse_event(self, response):
        sel = response.css('html')
        content = sel.css('div.conference-lead-info')
        item = response.meta['item']
        item['source'] = response.request.url
        item['event_website'] = ''
        # item['title'] = content.css('div.conference-lead-info h1.title::text').extract()
        try:
            item['description'] = content.css('div.field-name-body div.field-item p:first-child::text').extract()[0].strip()
        except Exception as e:
            item['description'] = ''
        pass
        item['addressRegion'] = ''
        item['postalCode'] = ''
        item['price_range'] = ''
        item['addressLocality'] = content.css('div.field-name-field-conf-venues a::text').extract()[0].strip()
        item['location'] = ''
        item['category'] = 'Conference'
        item['industry'] = 'Event'

        item['date'] = content.css('div.conference-dates div div::text').extract()[1]

        self.get_event_date(item)

        loc = self.google_maps.search(location=item['addressLocality'])
        my_location = loc.first()

        try:
            item['country_code'] = my_location.country_shortcut
            item['addressCountry'] = my_location.country_shortcut
            item['city'] = my_location.city
            item['longitude'] = my_location.lng
            item['latitude'] = my_location.lat
            item['streetAddress'] = my_location.formatted_address
        except Exception as e:
            item['country_code'] = ''
            item['city'] = ''
            item['longitude'] = ''
            item['latitude'] = ''
            item['streetAddress'] = ''
        pass
        yield item

    def init_Month(self):
        self.month = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                      'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11',
                      'December': '12'}

    def get_event_date(self, item):
        item['event_start'] = '0000-00-00 00:00:0'
        item['event_end'] = '0000-00-00 00:00:0'
        raw_date = item['date']
        try:
            year_date = raw_date.split(',')
            month_days = (year_date[0]).split('-')

            from_date = (month_days[0]).split(' ')

            from_month = (from_date[0]).strip()
            from_day = (from_date[1]).strip()

            to_date = (month_days[1]).split(' ')
            if len(to_date) == 1:
                to_day = (to_date[0]).strip()
                to_month = from_month
            else:
                to_month = (to_date[0]).strip()
                to_day = (to_date[1]).strip()

            year = (year_date[1]).strip()

            from_month = self.month[from_month]
            to_month = self.month[to_month]

            from_date = year + '-' + from_month + '-' + from_day + 'T10:00:00'
            to_date = year + '-' + to_month + '-' + to_day + 'T10:00:00'

            print from_date + ' '
            print to_date + ' '

            event_start = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            event_end = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            item['event_start'] = event_start
            item['event_end'] = event_end

        except Exception as e:
            item['event_start'] = '0000-00-00 00:00:0'
            item['event_end'] = '0000-00-00 00:00:0'
        pass
