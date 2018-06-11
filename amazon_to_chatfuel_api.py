# -*- encoding: utf-8 -*-

import json
import xmltodict
import bottlenose

from collections import OrderedDict
from flask import Flask, jsonify, request, current_app


# Your Access Key ID, as taken from the Your Account page
AWS_ACCESS_KEY_ID = "AKIAJ3P3X7UGTI2QF2YA"

# Your Secret Key corresponding to the above ID,
# as taken from the Your Account page
AWS_SECRET_ACCESS_KEY = "AXzurPGEYhf9E4GHiGh/2Y/chYlNqd+a3b1cw0Js"

# Your Associate Tag
AWS_ASSOCIATE_TAG = "worldcup-20"

link = "https://amazon-to-chatfuel-api.herokuapp.com"


def queryToGetASINs(searchterm):
    """Accepts search term and searches it through Amazon API
        and returns ASINs of first 9 product

    Keyword Arguments:
            searchterm {str} -- search term that you want to search on Amazon

    Returns:
            [list] -- first 9 ASINs that are returned by Amazon API
                        of the search term
    """
    amazon = bottlenose.Amazon(
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    xml_data = amazon.ItemSearch(Keywords=searchterm, SearchIndex="All")
    o = xmltodict.parse(xml_data)
    json_data = json.dumps(o)
    dict_data = json.loads(json_data)
    products = dict_data['ItemSearchResponse']['Items']['Item']
    ASINs = []
    for i in range(0, 9):
        ASINs.append(products[i]['ASIN'])

    return ASINs


app = Flask(__name__, static_folder="static")


@app.route('/detail/<keyword>')
def sendList(keyword):
    """search key word on Amazon.com and return JSON API

    Arguments:
        keyword {str} -- keyword that will be searched on Amazon

    Returns:
        flask.current_app -- returns JSON as response with MIME
    """
    # Get 9 ASINs for search term passed as searchterm below
    ASINs = queryToGetASINs(searchterm=keyword)
    print(ASINs)
    if ASINs:
        json_temp = OrderedDict()
        messages = OrderedDict()
        attachment = OrderedDict()
        payload = OrderedDict()
        message = []

        payload['template_type'] = 'generic'
        payload['image_aspect_ratio'] = 'square'
        payload['elements'] = CreateElement(ASINs)

        attachment['type'] = "template"
        attachment['payload'] = payload

        messages['attachment'] = attachment
        message.append(messages)

        json_temp["messages"] = message

    return current_app.response_class(
        json.dumps(json_temp, indent=4, separators=(',', ': ')) + '\n',
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )


def CreateElement(list_name):

    elements = []

    for i in list_name:
        print("************ = {}".format(i))
        element = OrderedDict()

        # Get required data using ASIN number
        url, title, image, description = GetData(i)

        # Create an Element
        element["title"] = title[:80]
        element["image_url"] = image
        element["subtitle"] = description[:80]

        # Default Action
        default_action = OrderedDict()
        default_action["type"] = "web_url"
        default_action["url"] = url
        default_action["messenger_extensions"] = True
        element["default_action"] = default_action

        # Button of product
        button = []
        button_1 = OrderedDict()
        button_1["type"] = "web_url"
        button_1["url"] = url
        button_1["title"] = "🎁 See on Amazon"
        button.append(button_1)
        element["buttons"] = button

        # Add Element to Elements
        elements.append(element)
    print(elements)
    return elements


def GetData(asin):
    amazon = bottlenose.Amazon(
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    xml_data = amazon.ItemLookup(
        ItemId=asin, ResponseGroup="Images, ItemAttributes, Offers")
    o = xmltodict.parse(xml_data)
    json_data = json.dumps(o)
    dict_data = json.loads(json_data)
    print(asin)

    # Title of the Product
    title = dict_data['ItemLookupResponse']['Items']['Item'][
        'ItemAttributes']['Title']

    # Image of the Product
    try:
        image = dict_data['ItemLookupResponse']['Items']['Item'][
            'LargeImage']['URL']
    except KeyError:
        images = dict_data['ItemLookupResponse']['Items']['Item'][
            'ImageSets']['ImageSet'][0]
        for key, values in images.iteritems():
            if key.endswith('Image'):
                image = values['URL']
    except:
        # Set Default Product Image URL if Amazon don not have product Image
        image = ''

    # Description of the product
    try:
        descr = dict_data['ItemLookupResponse']['Items']['Item'][
            'ItemAttributes']['Feature']
        description = " ".join(str(x) for x in descr)
    except KeyError:
        description = ''

    url = dict_data['ItemLookupResponse']['Items']['Item']['DetailPageURL']

    return url, title, image, description


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RV'
if __name__ == "__main__":
    app.run(port=9000)
