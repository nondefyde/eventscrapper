import scrapy
from datetime import datetime
from datetime import date
from geolocation.main import GoogleMaps
import json
from myscrapper.items import EventItem


class EventEyeSpider(scrapy.Spider):
    google_maps = ''
    month = []

    name = "eventeye"
    allowed_domains = ["eventseye.com"]
    start_urls = ['http://www.eventseye.com/fairs/Upcoming_Trade_Shows.html']
    # start_urls = []

    def __init__(self, **kwargs):
        super(EventEyeSpider, self).__init__(**kwargs)
        self.init_Month()

        # self.urls = self.get_dict('assets\event_eye_start_urls.json')
        # for url in self.urls:
        #     self.start_urls = self.start_urls + [url['url']]

        self.google_maps = GoogleMaps(api_key='AIzaSyCaxLzZ2r7AbCJiIy5RtJ4jOQXcOlDbeV0')

    def parse(self, response):
        urls = response.css('table td.mtb a::attr(href)').extract()
        for url in urls:
            item = EventItem()
            item['url'] = 'http://www.eventseye.com'+url
            print url
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request

    def print_start_urls(self, response):
        urls = response.css('table td.mtb a::attr(href)').extract()
        for url in urls:
            item = EventItem()
            item['url'] = url
            yield item

    def parse_event(self, response):
        sel = response.css('html')
        item = EventItem()
        item['event_website'] = 'http://www.eventseye.com/'
        item['url'] = response.request.url
        item['source'] = sel.css('table td.mt a[rel="nofollow"]::attr(href)').extract()[0].strip()
        item['title'] = sel.css('table table h1 b::text').extract()[0]
        item['description'] = ''
        item['addressRegion'] = ''
        item['price_range'] = ''
        item['addressLocality'] = sel.css('table a font.etb::text').extract()[0]
        item['location'] = sel.css('table table h1 b::text').extract()[0]
        item['date'] = sel.css('table td.mt:first-child span::text').extract()[0].strip()
        state_code = sel.css('table td.mt span a::attr(href)').extract()[0].strip()

        state_code = (state_code[state_code.rindex('-')+1:state_code.index('.')]).upper()
        item['state_code'] = state_code

        item['category'] = 'Cant Figure this out'
        item['industry'] = 'Cant Figure this out'


        self.get_datetime(item)

        loc = self.google_maps.search(location=item['addressLocality'])
        my_location = loc.first()
        try:
            item['postalCode'] = my_location.postal_code
            item['country_code'] = my_location.country_shortcut
            item['addressCountry'] = my_location.country_shortcut
            item['city'] = my_location.city
            item['longitude'] = my_location.lng
            item['latitude'] = my_location.lat
            item['streetAddress'] = my_location.formatted_address
        except Exception as e:
            item['postalCode'] = ''
            item['country_code'] = ''
            item['city'] = ''
            item['longitude'] = ''
            item['latitude'] = ''
            item['streetAddress'] = ''
        pass

        yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def init_Month(self):
        self.month = {'Jan': '01', 'Feb': '02', 'March': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jly': '07',
                      'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    def get_datetime(self, item):
        item['event_start'] = '0000-00-00 00:00:0'
        item['event_end'] = '0000-00-00 00:00:0'
        date = item['date']
        try:
            check = date.split('.')
            if len(check) == 2:
                dot_index = date.index(".")
                comma_index = date.index(",")

                days = date[dot_index+1:comma_index]
                days = days.split('-')

                from_day = (days[0]).strip()
                to_day = (days[1]).strip()

                year = (date[comma_index+1:]).strip()
                month_str = (date[0:dot_index]).strip()

                month = self.month[month_str]

                from_date = year+'-'+month+'-'+from_day+'T10:00:00'
                to_date = year+'-'+month+'-'+to_day+'T10:00:00'

                event_start = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                event_end = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

                item['event_start'] = event_start
                item['event_end'] = event_end

            else:
                comma_index = date.index(",")

                year = (date[comma_index+1:]).strip()

                days = date.split('-')
                from_month_str = (days[0].strip())[0:3]
                to_month_str = (days[1].strip())[0:3]

                for_days = date.split(',')
                for_days = for_days[0]
                for_days = for_days[for_days.index('.')+1:]
                for_days = for_days.split(to_month_str)

                from_day = (for_days[0]).strip()
                from_day = from_day[0:2]
                to_day = (for_days[1]).strip()
                to_day = to_day.split(' ')
                to_day = to_day[1]

                from_month = self.month[from_month_str]
                to_month = self.month[to_month_str]

                from_date = year+'-'+from_month+'-'+from_day+'T10:00:00'
                to_date = year+'-'+to_month+'-'+to_day+'T10:00:00'

                event_start = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                event_end = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

                item['event_start'] = event_start
                item['event_end'] = event_end

        except Exception as e:
            item['event_start'] = '0000-00-00 00:00:0'
            item['event_end'] = '0000-00-00 00:00:0'
        pass
