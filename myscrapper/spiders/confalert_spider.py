import scrapy
from datetime import datetime
from geolocation.main import GoogleMaps
import json
from myscrapper.items import EventItem


class ConferenceAlertsSpider(scrapy.Spider):
    urls = ''
    google_maps = ''
    month = []

    name = "conf"
    allowed_domains = ["conferencealerts.com"]
    start_urls = []

    def __init__(self, **kwargs):
        super(ConferenceAlertsSpider, self).__init__(**kwargs)
        self.init_month()
        self.urls = self.get_dict('assets\conf_start_urls.json')
        for url in self.urls:
            self.start_urls = self.start_urls + [url['url']]

        self.google_maps = GoogleMaps(api_key='AIzaSyCaxLzZ2r7AbCJiIy5RtJ4jOQXcOlDbeV0')

    def parse(self, response):
        sel = response.css('table#searchResultTable tr td')

        title = sel.css('span#searchName a::text').extract()
        source = sel.css('span#searchName a::attr(href)').extract()
        location = sel.css('span#searchPlace::text').extract()
        country = sel.css('span#searchPlace span::text').extract()

        for num in range(0, len(title)):
            item = EventItem()
            item['url'] = response.request.url
            item['source'] = 'http://conferencealerts.com/' + source[num]
            item['title'] = title[num]
            item['category'] = 'Conference'
            item['industry'] = item['category']
            item['location'] = location[num]
            item['addressCountry'] = country[num]
            item['addressLocality'] = location[num] + '' + country[num]
            item['addressRegion'] = ''
            item['price_range'] = ''

            request = scrapy.Request(item['source'], callback=self.parse_event,
                                     meta={'item': item})
            yield request

    def parse_event(self, response):
        item = response.meta['item']
        sel = response.css('div#eventInfoContainer table')

        description = sel.css('span#eventDescription::text').extract()
        event_website = sel.css('span#eventWebsite a::attr(href)').extract()
        date = sel.css('span#eventDate::text').extract()
        item['description'] = description[0]
        item['event_website'] = event_website[0]
        item['date'] = date[0]
        item['postalCode'] = ''

        self.get_datetime(item)

        loc = self.google_maps.search(location=item['addressLocality'])
        my_location = loc.first()

        try:
            item['country_code'] = my_location.country_shortcut
            item['longitude'] = my_location.lng
            item['latitude'] = my_location.lat
            item['streetAddress'] = my_location.formatted_address
        except Exception as e:
            item['country_code'] = ''
            item['longitude'] = ''
            item['latitude'] = ''
            item['streetAddress'] = ''
        pass

        yield item

    def print_start_urls(self, response):
        for href in response.css('div.topicTableColumn1Container table td, div.topicTableColumn2Container table td'):
            url = href.css('a::attr(href)').extract()
            if len(url) == 0 or url[0] == '#top':
                continue
            url = 'http://conferencealerts.com/' + url[0]

            item = EventItem()
            item['url'] = url
            yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def init_month(self):
        self.month = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                      'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11',
                      'December': '12'}

    def get_datetime(self, item):
        date = item['date']
        try:
            tokens = date.split(' ')

            from_day = (tokens[0]).strip()
            from_day = from_day[0:1]
            to_day = (tokens[4]).strip()
            to_day = to_day[0:1]

            year = tokens[6]

            month = tokens[5]
            month = month.strip()
            month = self.month[month]

            print from_day + ' ' + to_day + ' ' + month + ' ' + year

            from_date = year + '-' + month + '-' + from_day + 'T10:00:00'
            to_date = year + '-' + month + '-' + to_day + 'T10:00:00'

            event_start = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            event_end = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            item['event_start'] = event_start
            item['event_end'] = event_end

        except Exception as e:
            item['event_start'] = '0000-00-00 00:00:0'
            item['event_end'] = '0000-00-00 00:00:0'
        pass
