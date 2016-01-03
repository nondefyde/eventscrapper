import json
from twisted.enterprise import adbapi
import MySQLdb.cursors
import logging


class SQLandJsonStoragePipeline(object):
    categories = "categories"
    industries = "industries"
    countries = "countries"
    states = "states"

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', db='eventbrite',
                                            user='root', passwd='', cursorclass=MySQLdb.cursors.DictCursor,
                                            charset='utf8', use_unicode=True)
        # self.file = open('items.json', 'wb')

        self.categories = self.get_dict('data\categories.json')
        self.industries = self.get_dict('data\industries.json')
        self.countries = self.get_dict('data\countries.json')
        self.states = self.get_dict('data\states.json')

    def process_item(self, item, spider):
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)

        # self._print_to_json_file(item)

        return item

    def _print_to_json_file(self, item):

        self.get_ids(item)
        self.get_country_code(item)
        self.get_state_code(item)
        self.get_industry_id(item)

        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)

    def _conditional_insert(self, tx, item):

        self.get_ids(item)
        self.get_country_code(item)
        self.get_state_code(item)
        self.get_industry_id(item)

        # all this block run on it's own thread
        tx.execute("select * from test where source = %s", (item['source'],))
        result = tx.fetchone()
        if result:
            logging.log(logging.INFO, "Item already stored in db: %s" % item)
        else:
            tx.execute(
                "insert into test (title, description, source, category_id, address_1, price_range, country_code, "
                "state_code, city, event_website, zip, event_start, event_end, latitude, longitude, location)"
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item['title'], item['description'], item['source'], item['category_id'],
                 item['streetAddress'], item['price_range'],item['country_code'], item['state_code'],
                 item['addressLocality'], item['event_website'], item['postalCode'],item['event_start'],
                 item['event_end'], item['latitude'], item['longitude'], item['location'])
            )
            logging.log(logging.INFO, "Item stored in db: %s" % item)

    def handle_error(self, e):
        logging.log(logging.ERROR, e)

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def get_ids(self, item):
        # get the category id given the string
        categories = self.categories
        category_id = 0
        for category in categories:
            cat = category['category']
            cat2 = item['category']
            if cat.lower() == cat2.lower():
                category_id = category['id']
        item['category_id'] = category_id

    def get_country_code(self, item):
        countries = self.countries
        country_code = item['addressCountry']
        for country in countries:
            con = country['name']
            con2 = item['addressCountry']
            if con.lower() == con2.lower():
                country_code = country['iso3']
        item['country_code'] = country_code

    def get_state_code(self, item):
        states = self.states
        state_code = item['addressRegion']
        for state in states:
            con = state['name']
            con2 = item['addressRegion']
            if con.lower() == con2.lower():
                state_code = state['abbrev']
        item['state_code'] = state_code

    def get_industry_id(self, item):
        industries = self.industries
        industry_id = 0
        for industry in industries:
            con = industry['industry']
            con2 = item['industry']
            if con.lower() == con2.lower():
                industry_id = industry['id']
        item['industry_id'] = industry_id


class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('test.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class JsonStartUrlWriterPipeline(object):

    def __init__(self):
        self.file = open('assets\event_eye_start_urls.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
