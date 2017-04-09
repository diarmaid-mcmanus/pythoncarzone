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
        def try_except(success, failure, thing):
            try:
                return success[thing]
            except KeyError:
                return failure

        all_data = json.loads(response.text)
        vehicles = all_data['results']
        for vehicle in vehicles:
            try:
                yield {
                    'id': vehicle['id'],
                    'url': vehicle['url'],
                    'make': vehicle['make'],
                    'model': vehicle['model'],
                    'features': vehicle['features'],
                    'mileage': try_except(vehicle, None, 'km'),
                    'engine': try_except(vehicle, None, 'engine'),
                    'price': vehicle['price'],
                    'year': try_except(vehicle, None, 'year')
                }
                yield scrapy.Request(vehicle['url'], callback=self.car_details_parse)
            except:
                from scrapy.shell import inspect_response
                inspect_response(response, self)

        if self.current_page < all_data['state']['totalPageNumber']:
            # increment 1 to the current page, format the URL, yield to scrapy
            next_page = self.ajax_url.format(self.current_page+1)
            yield scrapy.Request(next_page, callback=self.parse)

        self.current_page += 1

    def car_details_parse(self, response):
        vehicle_data_html = response.css('script#data::text').extract_first()
        vehicle_data_trimmed = vehicle_data_html[16:]
        all_data = json.loads(vehicle_data_trimmed)
        try:
            yield {
                'id': all_data['result']['id'],
                'image_urls': all_data['result']['largeImageUrls']
            }
        except: # TODO no images.
            yield {
                'id': all_data['result']['id'],
                'image_urls': []
            }