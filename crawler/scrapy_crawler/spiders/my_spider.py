import scrapy
import re
import datetime
import sqlite3
import os
import jsonschema
from urllib import request
import xmltodict
from xml.parsers.expat import ExpatError

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
        try:
            xml_dict = xmltodict.parse(xml_str)
        except ExpatError:
            return
        profile_dict = xml_dict['schema']['Profile']
        # get the name
        first_name = profile_dict['Names']['FirstName']['@value']
        sir_name = profile_dict['Names']['SirName']['@value']
        last_name = profile_dict['Names']['FamilyName']['@value']
        processed_name = f'{first_name} {sir_name} {last_name}'
        # get avatar url
        try:
            avatar_address = 'https://parliament.bg' + response.css('.MPBlock_columns2 > img::attr(src)').get()
        except TypeError:
            return
        # place and date of birth
        place_of_birth_raw = profile_dict['PlaceOfBirth']['@value']
        date_of_birth_str = profile_dict['DateOfBirth']['@value']
        place_of_birth_raw = place_of_birth_raw.split(',')
        date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%d/%m/%Y').date()
        place_of_birth = place_of_birth_raw[0].strip()
        country_of_birth = place_of_birth_raw[1].strip()
        # job
        try:
            job = profile_dict['Profession']['Profession']['@value']
        except TypeError:
            job = 'No data'
        # languages
        try:
            languages_raw = profile_dict['Language']['Language']
        except TypeError:
            languages_raw = {}
            languages_raw['@value'] = 'No data'
        languages = []
        for item in languages_raw:
            if isinstance(item, str):
                languages.append(languages_raw['@value'])
            else:
                languages = [item['@value'] for item in languages_raw]
        # election party
        elected_from = profile_dict['PoliticalForce']['@value']
        percentage_regex = r'\d\d?.\d{2}%'
        elected_from = re.sub(percentage_regex, '', elected_from).strip()
        # email
        email = profile_dict['E-mail']['@value']
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
