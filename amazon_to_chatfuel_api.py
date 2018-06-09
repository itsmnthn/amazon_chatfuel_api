# -*- encoding: utf-8 -*-

import json
import xmltodict
import bottlenose

from flask import Flask, jsonify, request


# Your Access Key ID, as taken from the Your Account page
AWS_ACCESS_KEY_ID = "AKIAJUB2GKHOEXPHACDQ"

# Your Secret Key corresponding to the above ID,
# as taken from the Your Account page
AWS_SECRET_ACCESS_KEY = "UFggpYybRfa4ba5ZZ6G8qk/iP8pySLWTcFAn1r95"

# Your Associate Tag
AWS_ASSOCIATE_TAG = "uberminicourse-20"

link = "https://amazon123-app.herokuapp.com/"


def queryToGetASINs(searchterm="iphone"):
    """Accepts search term and searches it through Amazon API
        and returns ASINs of first 9 product

    Keyword Arguments:
            searchterm {str} -- search term that you want to search on
                        Amazon (default: {"iphone"})

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
    """This function called vai URL

    Arguments:
        keyword {str} -- search term

    Returns:
        jsonify -- json object that contains json output
    """
    # Get 9 ASINs for search term passed as searchterm below
    ASINs = queryToGetASINs(searchterm=keyword)
    print(ASINs)
    if ASINs:
        send = {
            "messages": [
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                                "template_type": "generic",
                                "image_aspect_ratio": "square",
                                "elements": CreateElement(ASINs)
                        }
                    }
                }
            ]
        }
    return jsonify(send)


def CreateElement(list_name):

    elements = []

    for i in list_name:
        print("************ = {}".format(i))
        element = {}

        # Get required data using ASIN number
        url, title, image, description = GetData(i)

        # Create an Element
        element["title"] = title[:80]
        element["image_url"] = image
        element["subtitle"] = description[:80]

        # Default Action
        default_action = {}
        default_action["type"] = "web_url"
        default_action["url"] = url
        default_action["messenger_extensions"] = True
        element["default_action"] = default_action

        # Button of product
        button = []
        button_1 = {}
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