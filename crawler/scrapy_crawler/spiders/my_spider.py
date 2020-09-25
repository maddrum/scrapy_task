import scrapy
import re
import datetime
import sqlite3
import os
import jsonschema
from urllib import request
import xml.etree.ElementTree as ET

# get the database
database_path = os.path.dirname(__file__)
database_path = os.path.dirname(database_path)
database_path = os.path.dirname(database_path)
database_path = os.path.dirname(database_path)
database_path = os.path.join(database_path, 'django_scrapy_task', 'db.sqlite3')
# connect to database
conn = sqlite3.connect(database_path)


class BulgarianMPSpider(scrapy.Spider):
    name = 'mp'
    start_urls = [
        'https://parliament.bg/bg/MP/',
    ]

    def parse(self, response, **kwargs):
        sub_info = response.css('.MPBlock > div > div > a')
        yield from response.follow_all(sub_info, self.parse_mp)

    def parse_mp(self, response):
        """Returns:
        {
            'name': Full name /string/,
            'avatar': Picture URL /string/,
            'country_of_birth': Country of birth /string/,
            'place_of_birth': Place of birth /string/,
            'date_of_birth': Date of birth /datetime MM-DD-YYYY/,
            'languages': Languages /list of strings/,
            'job': Job /string/,
            'political_party: Elected from political party /string/
            'email': E-Mail /email/,
        }
        """
        # xml_parse
        mp_id = response.url.split('/')[-1]
        xml_address = 'https://parliament.bg/export.php/bg/xml/MP/' + mp_id
        xml_str = request.urlopen(xml_address).read()
        xml_root = ET.fromstring(xml_str)
        for element in xml_root.findall('Profile'):
            print(element)
            print(element.tag, element.attrib)
        # get the name
        raw_name_string = str(response.css('.MProwD').get())
        name_pattern = r'</?(\w+| |=|\")+>+'
        processed_name = re.sub(name_pattern, '', raw_name_string).strip()
        # get avatar url
        try:
            avatar_address = 'https://parliament.bg' + response.css('.MPBlock_columns2 > img::attr(src)').get()
        except:
            avatar_address = 'No data'
        # initial information cleanup
        info_raw = str(response.css('.frontList').get())
        info_raw = info_raw.replace('</li>', '')
        info_raw = info_raw.replace('</ul>', '')
        info_raw = info_raw.split('<li>')
        info_raw = info_raw[1:]
        if len(info_raw) == 0:
            return
        # checks for language and job listed and fill in
        if not info_raw[1].split(':')[0].strip() == 'Професия':
            info_raw.insert(1, 'No data')
        if not info_raw[2].split(':')[0].strip() == 'Езици':
            info_raw.insert(2, 'No data')
        # place and date of birth
        place_of_birth_raw = info_raw[0].split(':')[-1].split(',')
        country_of_birth = place_of_birth_raw[-1].strip()
        place_and_date_of_birth = place_of_birth_raw[0].strip()
        # using re to get the date and and the place
        date_regex = r'\d{2}\/\d{2}\/\d{4}'
        date_of_birth_str = re.search(date_regex, place_and_date_of_birth).group(0)
        place_of_birth = re.sub(date_regex, '', place_and_date_of_birth).strip()
        date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%d/%m/%Y').date()
        # job
        job = info_raw[1].split(':')[-1].replace(';', ' ').strip()
        # languages
        languages = info_raw[2].split(':')[-1].replace(';', ',').strip()
        if languages[-1] == ',':
            languages = languages[:-1]
        languages = languages.split(",")
        # election party
        elected_from = info_raw[3].split(':')[-1]
        elected_from = elected_from.replace(';', '').strip()
        percentage_regex = r'\d\d?.\d{2}%'
        elected_from = re.sub(percentage_regex, '', elected_from).strip()
        # email
        email = info_raw[-1].split('mailto:')[1].split("\"")[0].strip()
        # result data
        result_data = {
            'name': processed_name,
            'avatar': avatar_address,
            'country_of_birth': country_of_birth,
            'place_of_birth': place_of_birth,
            'date_of_birth': date_of_birth,
            'languages': languages,
            'job': job,
            'political_party': elected_from,
            'email': email,
        }
        json_test = self.validate_schema(result_data)
        if not json_test:
            print(f"[NOTIFICATION] JSON SCHEMA validation FAILED for {result_data['name']}, SKIPPING...")
            return
        self.popup_database(result_data)
        yield result_data

    def popup_database(self, crawl_data):
        """
        Writes scraped data to database. Check if data exists and skips that record.
        :param crawl_data: - result of scraping
        :return: nothing
        """

        # check if already crawled and skip writing the record
        check_database = conn.execute(f"SELECT name FROM crawler_app_scrapeddata WHERE name='{crawl_data['name']}'")
        if check_database.fetchone():
            print(f"[NOTIFICATION] {crawl_data['name']} already scraped, skipping this record...")
            return
        execution_command = f"INSERT INTO crawler_app_scrapeddata (" \
                            f"name, " \
                            f"avatar, " \
                            f"country_of_birth, " \
                            f"place_of_birth, " \
                            f"date_of_birth, " \
                            f"job, " \
                            f"languages, " \
                            f"political_party, " \
                            f"email, " \
                            f"created_on, " \
                            f"edited_on" \
                            f") " \
                            f"VALUES(" \
                            f"'{crawl_data['name']}', " \
                            f"'{crawl_data['avatar']}', " \
                            f"'{crawl_data['country_of_birth']}', " \
                            f"'{crawl_data['place_of_birth']}', " \
                            f"'{crawl_data['date_of_birth']}', " \
                            f"'{crawl_data['job']}', " \
                            f"'{','.join(crawl_data['languages'])}', " \
                            f"'{crawl_data['political_party']}', " \
                            f"'{crawl_data['email']}', " \
                            f"'{str(datetime.datetime.now())}', " \
                            f"'{str(datetime.datetime.now())}'" \
                            f")"
        conn.execute(execution_command)
        conn.commit()

    def validate_schema(self, crawl_data):
        schema = {
            "name": {"type": "string"},
            "avatar": {"type": "string"},
            "country_of_birth": {"type": "string"},
            "place_of_birth": {"type": "string"},
            "date_of_birth": {"type": "string"},
            "languages": {"type": ["array", "string"]},
            "job": {"type": "string"},
            "political_party": {"type": "string"},
            'email': {"type": "string"},
        }
        try:
            jsonschema.validate(instance=crawl_data, schema=schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True
