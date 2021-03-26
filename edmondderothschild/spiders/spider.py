import re

import scrapy

from scrapy.loader import ItemLoader
from scrapy.spiders import XMLFeedSpider
from w3lib.html import remove_tags

from ..items import EdmondderothschildItem
from itemloaders.processors import TakeFirst

import requests
import xmltodict

class EdmondderothschildSpider(XMLFeedSpider):
	name = 'edmondderothschild'
	start_urls = ['https://news.edmond-de-rothschild.com/api/ComNewsClient/News/GetAll?languageCode=fr&idPictureFormat=2&countryId=1&pageSize=999999&pageIndex=0&tags=undefined&businessId=undefined']
	itertag = 'IdNewsContent'

	def parse_node(self, response, node):
		_id = node.xpath('//text()').get()
		url = f'https://news.edmond-de-rothschild.com/api/ComNewsClient/News/GetByID?IdNews={_id}'
		yield scrapy.Request(url, callback=self.parse_link)

	def parse_link(self, response):
		# data = scrapy.Selector(response, type='xml')
		data = response.xpath('//*').get()
		title = re.findall(r'<Title>(.*?)</Title>', data, re.DOTALL)[0]
		date = re.findall(r'<PublishingDate>(.*?)</PublishingDate>', data, re.DOTALL)[0]
		description = re.findall(r'<Content>(.*?)</Content>', data, re.DOTALL)[0]
		dict_of_chars = {'#58;': ':', 'quot;': '"', '#160;': '', '&lt;': '<', '&gt;': '>', '&amp;': '', 'bull;': '', 'acute;': '´', 'grave;': '`', 'rsquo;': '`', 'circ;': 'ˆ', 'nbsp;': ' '}
		for char in dict_of_chars:
			description = re.sub(rf'{char}', f'{dict_of_chars[char]}', description)
		description = remove_tags(description)
		print(description)

		item = ItemLoader(item=EdmondderothschildItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
