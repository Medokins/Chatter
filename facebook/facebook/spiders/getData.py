import scrapy
from scrapy.http import FormRequest
from scrapy import Selector
import pandas as pd

class FacebookSpider(scrapy.Spider):
    """
    Parse FB pages (needs credentials)
    """
    name = "getData"

    def __init__(self, email='', password='',  **kwargs):
        super(FacebookSpider, self).__init__(**kwargs)

        self.dict = {}

        self.Name=[]
        self.Text=[]
        self.Time=[]

        if not email or not password:
            raise ValueError("You need to provide valid email and password!")
        else:
            self.email = email
            self.password = password

        self.start_urls = ["https://facebook.com/messages"]

    def parse(self, response):
        return FormRequest.from_response(
                response,
                formxpath='//form[contains(@action, "login")]',
                formdata={'email': self.email,'pass': self.password},
                callback=self.parse_home
        )

    def parse_home(self, response):
        href = "https://facebook.com/messages"
        return scrapy.Request(
            url=href,
            callback=self.parse_page,
        )

    def parse_page(self, response):
        res = response.body
        people = Selector(text=res).xpath('//h3/a/text()').extract()
        people_link = Selector(text=res).xpath('//h3/a/@href').extract()
        print("People:\n\n", people)
        print("people_links:\n\n", people_link)
        # print('Choose the conversation')
        # print(peoples, people_link)
        # for i in range(len(peoples)):
        #     print(i,peoples[i])
        # convo = int(input())

        # yield scrapy.Request(url="https://facebook.com/messages"+ people_link[convo], callback=self.parse_convo)

    def parse_convo(self,response):
        yield