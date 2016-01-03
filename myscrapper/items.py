# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventItem(scrapy.Item):
    event_website = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    event_start = scrapy.Field()
    event_end = scrapy.Field()
    date = scrapy.Field()
    price_range = scrapy.Field()

    category = scrapy.Field()
    category_id = scrapy.Field()

    industry = scrapy.Field()
    industry_id = scrapy.Field()

    country_code = scrapy.Field()
    state_code = scrapy.Field()

    latitude = scrapy.Field()
    longitude = scrapy.Field()

    city = scrapy.Field()
    location = scrapy.Field()
    address_1 = scrapy.Field()

    name = scrapy.Field()
    addressCountry = scrapy.Field()
    addressRegion = scrapy.Field()
    addressLocality = scrapy.Field()
    streetAddress = scrapy.Field()
    postalCode = scrapy.Field()

    pass