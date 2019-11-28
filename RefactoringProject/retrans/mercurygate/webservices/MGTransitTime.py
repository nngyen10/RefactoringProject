'''
Created on Jan 24, 2013

@author: michaelbartz
'''

from django.conf import settings
import math

from lxml import etree
import requests


from transsendlib.TransSendUtil import TransSendUtil
from transsend.models import GoogleTransitTimeCall, MasterAddress


SOAP_HEADER = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Header/><SOAP-ENV:Body>"""
XML_HEADER = """<?xml version="1.0"?>"""
SOAP_TRAILER = """</SOAP-ENV:Body></SOAP-ENV:Envelope>"""
EXTRAS = {'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba', 'NB': 'New Brunswick', 'NL': 'Newfoundland', 'NS': 'Nova Scotia',
          'ON': 'Ontario', 'PE': 'Prince Edward Island', 'QC': 'Quebec', 'SK': 'Saskatchewan', 'NT': 'Northwest Territories', 'YT': 'Yukon',
          'NU': 'Nunavut', 'HI': 'Hawaii', 'PR': 'Puerto Rico', 'AK': 'Alaska', }

PROXIES = settings.PROXIES


def GoogleServiceDays(order):
    url = "https://maps.googleapis.com/maps/api/distancematrix/xml?key="
    miles = 0.0
    msg = '';
    try:
        if order.shipper.stateprovince.upper() not in ['HI', 'PR', '', ] and order.consignee.stateprovince.upper() not in ['HI', 'PR', '', ]:
            try:
                shipper_zips = MasterAddress.objects.filter(city=order.shipper.city.upper()).filter(stateprovince=order.shipper.stateprovince.upper())
                shipper_zips = [i.postalcode.upper().replace(' ', '') for i in shipper_zips]
            except:
                msg = 'Ordernumber: %s\nOwner: %s\nShipper: %s, %s, %s, %s %s' % (order.ordernumber, order.billee.name, order.shipper.name, order.shipper.address1, order.shipper.city, order.shipper.stateprovince, order.shipper.postalcode)
                print msg
            from_addr = []
            from_addr.append(order.shipper.city.capitalize().replace(' ', '+'))
            from_addr.append(order.shipper.stateprovince.upper())

            to_addr = []
            to_addr.append(order.consignee.city.capitalize().replace(' ', '+'))
            to_addr.append(order.consignee.stateprovince.upper())
            try:
                consignee_zips = MasterAddress.objects.filter(city=order.consignee.city.upper()).filter(stateprovince=order.consignee.stateprovince.upper())
                consignee_zips = [i.postalcode.upper().replace(' ', '') for i in consignee_zips]
            except:
                msg = 'Ordernumber: %s\nOwner: %s\nConsignee: %s, %s, %s, %s %s' % (order.ordernumber, order.billee.name, order.consignee.name, order.consignee.address1, order.consignee.city, order.consignee.stateprovince, order.consignee.postalcode)
                print msg
            if order.shipper.postalcode.isdigit():
                shipper_zip = order.shipper.postalcode[:5]
            else:
                shipper_zip = order.shipper.postalcode.upper().replace(' ', '')
            if shipper_zip in shipper_zips:
                from_addr.append(shipper_zip)
            else:
                if shipper_zips:
                    from_addr.append(shipper_zips[0])

            if order.consignee.postalcode.isdigit():
                consignee_zip = order.consignee.postalcode[:5]
            else:
                consignee_zip = order.consignee.postalcode.upper().replace(' ', '')
            if consignee_zip in consignee_zips:
                to_addr.append(consignee_zip)
            else:
                if consignee_zips:
                    to_addr.append(consignee_zips[0])

            url = url + settings.GOOGLE_API_KEY + "&origins="
            url = url + "+".join(from_addr) + "&destinations="
            url = url + "+".join(to_addr)
            page_xml = requests.get(url, proxies=PROXIES).content
            et = etree.fromstring(page_xml)
            if et.xpath('row/element/status')[0].text == 'OK':
                distance = float(et.xpath('row/element/distance/value')[0].text)
                miles = distance / 1000 * 0.621371
                servicedays = math.ceil(miles / 500)
            else:
                servicedays = 1.0
                msg = 'URL: %s\nOrdernumber: %s\nOwner: %s\nShipper: %s, %s, %s, %s %s' % (url, order.ordernumber, order.billee.name, order.shipper.name, order.shipper.address1, order.shipper.city, order.shipper.stateprovince, order.shipper.postalcode)
                msg = msg + '\nConsignee: %s, %s, %s, %s %s' % (order.consignee.name, order.consignee.address1, order.consignee.city, order.consignee.stateprovince, order.consignee.postalcode)
                print msg
        elif order.shipper.stateprovince.upper() in ['HI', 'PR', ] or order.consignee.stateprovince.upper() in ['HI', 'PR', ]:
            servicedays = 5.0
        else:
            servicedays = 5.0
            msg = 'Ordernumber: %s\nOwner: %s\nShipper: %s, %s, %s, %s %s' % (order.ordernumber, order.billee.name, order.shipper.name, order.shipper.address1, order.shipper.city, order.shipper.stateprovince, order.shipper.postalcode)
            msg = msg + '\nConsignee: %s, %s, %s, %s %s' % (order.consignee.name, order.consignee.address1, order.consignee.city, order.consignee.stateprovince, order.consignee.postalcode)
            print msg
    except Exception as e:
        servicedays = 1.0
        print e

    GoogleTransitTimeCall.objects.create(ordernumber=order.ordernumber, shipper_city=order.shipper.city,
                                         shipper_stateprovince=order.shipper.stateprovince, shipper_postalcode=order.shipper.postalcode,
                                         consignee_city=order.consignee.city, consignee_stateprovince=order.consignee.stateprovince,
                                         consignee_postalcode=order.consignee.postalcode, servicedays=servicedays, miles=miles)
    return servicedays

def GoogleServiceMiles(from_address, to_address):
    url = "https://maps.googleapis.com/maps/api/distancematrix/xml?key="
    miles = 0.0
    msg = ''
    try:
        if from_address.stateprovince.upper() not in ['HI', 'PR', '', ] and to_address.stateprovince.upper() not in ['HI', 'PR', '', ]:
            from_addr = []
            from_addr.append(from_address.city.capitalize().replace(' ', '+'))
            from_addr.append(from_address.stateprovince.upper())

            to_addr = []
            to_addr.append(to_address.city.capitalize().replace(' ', '+'))
            to_addr.append(to_address.stateprovince.upper())

            if from_address.postalcode.isdigit():
                shipper_zip = from_address.postalcode[:5]
            else:
                shipper_zip = from_address.postalcode.upper().replace(' ', '')
            from_addr.append(shipper_zip)

            if to_address.postalcode.isdigit():
                consignee_zip = to_address.postalcode[:5]
            else:
                consignee_zip = to_address.postalcode.upper().replace(' ', '')
            to_addr.append(consignee_zip)

            url = url + settings.GOOGLE_API_KEY + "&origins=" + "+".join(from_addr) + "&destinations=" + "+".join(to_addr)
            page_xml = requests.get(url).content
            et = etree.fromstring(page_xml)
            if et.xpath('row/element/status')[0].text == 'OK':
                print('OK')
                distance = float(et.xpath('row/element/distance/value')[0].text)
                miles = distance / 1000.0 * 0.621371
                servicedays = math.ceil(miles / 500)
                print("distance = {}".format(distance))
            else:
                print("Not OK")
                servicedays = 1.0
                msg = 'URL: %s\nShipper: %s, %s, %s, %s %s' % (url, from_address.name, from_address.address1, from_address.city, from_address.stateprovince, from_address.postalcode)
                msg = msg + '\nConsignee: %s, %s, %s, %s %s' % (to_address.name, to_address.address1, to_address.city, to_address.stateprovince, to_address.postalcode)
        elif from_address.stateprovince.upper() in ['HI', 'PR', ] or to_address.stateprovince.upper() in ['HI', 'PR', ]:
            servicedays = 5.0
        else:
            servicedays = 5.0
            msg = 'Shipper: %s, %s, %s, %s %s' % (from_address.name, from_address.address1, from_address.city, from_address.stateprovince, from_address.postalcode)
            msg = msg + '\nConsignee: %s, %s, %s, %s %s' % (to_address.name, to_address.address1, to_address.city, to_address.stateprovince, to_address.postalcode)    
    except Exception as e:
        ts_util.sendMessage(['transsendstatus@gmail.com', 'mbartz@re-trans.com', 'mferguson@re-trans.com'], 'Unknown Exception in MGTransitTime Google Distance API Returned 1.0 Days', 'URL: %s\n%s' % (url, str(e)))        
        servicedays = 1.0
    GoogleTransitTimeCall.objects.create(ordernumber='', shipper_city=from_address.city,
                                         shipper_stateprovince=from_address.stateprovince, shipper_postalcode=from_address.postalcode,
                                         consignee_city=to_address.city, consignee_stateprovince=to_address.stateprovince,
                                         consignee_postalcode=to_address.postalcode, servicedays=servicedays, miles=miles)
    return miles


