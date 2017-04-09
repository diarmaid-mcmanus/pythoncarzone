# -*- coding: utf-8 -*-
import scrapy
import json

class CarscraperSpider(scrapy.Spider):
    name = "carscraper"
    allowed_domains = ["carzone.ie"]
    ajax_url = 'http://www.carzone.ie/search/ajax-result/cars/page/{}/sort/price-asc/limit/30'
    start_urls = [ ajax_url.format(1) ]
    current_page = 1

    def parse(self, response):
        all_data = json.loads(response.text)
        vehicles = all_data['results']
        for vehicle in vehicles:
            yield {
                'id': vehicle['id'],
                'url': vehicle['url'],
            }

        if self.current_page < all_data['state']['totalPageNumber']:
            # increment 1 to the current page, format the URL, yield to scrapy
            next_page = self.ajax_url.format(self.current_page+1)
            yield scrapy.Request(next_page, callback=self.parse)

        self.current_page += 1