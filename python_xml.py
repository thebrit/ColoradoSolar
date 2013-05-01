#! /usr/bin/python
from __future__ import print_function
from __future__ import unicode_literals

import MySQLdb as mdb

#imports for email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
#import HTML
#from pyh import *
#from decimal import Decimal


#---------- Begin dict2rss ---------------------------------------------------------------------

#Modifications done to dict2rss allow xml files to be written for Google Merchant Center.
#Original code left for reference.
#Gary Atkinson Sept 2012

#from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
import cgi
from io import StringIO

# dict2rss written by Pascal Raszyk
# http://pastebucket.de/paste/749ce8de
#
# updates by Darryl Pogue
#   - 2010-11-25: Added Python 2.x and 3.x compatibility
#				 and output() function
# updates by Fredrik Wendt
#   - 2011-10-16: merged with example from polymetr at GitHub
#

class dict2rss:
	def __init__(self, dict):
		self.title = "Large Feed"
		self.version = "2.0"
		self.link = "http://www.solarpanelstore.com"
		#self.language = "en"
		self.description = "Everything you need to go Solar"
		self.itemio = StringIO()

		for key in dict:
		    Raise
			element = dict[key]
			if key == 'title': self.title = element
			elif key == 'version': self.version = element
			elif key == 'link': self.link = element
			#elif key == 'language': self.language = element
			elif key == 'description': self.description = element
			elif 'dict' in str(type(element)) and key == 'item':
				"""Parse Items to XML-valid Data"""

				sys.stdout = self.itemio
				for child in dict[key]:
					print(u'    <item>')
					for childchild in dict[key][child]:
						if childchild == "comment":
							print(u"      <!-- %s -->" % (dict[key][child][childchild]))
						else:
							try:
								if childchild in dict['cdata']:
									print(u'      <%s><![CDATA[%s]]></%s>'  % (childchild, cgi.escape(dict[key][child][childchild]), childchild))
								else:
									print(u'      <%s>%s</%s>'  % (childchild, cgi.escape(dict[key][child][childchild]), childchild))
							except: print(u'      <%s>%s</%s>'  % (childchild, cgi.escape(dict[key][child][childchild]), childchild))
					print(u'    </item>')

				sys.stdout = sys.__stdout__
		#print(self._out())
		#added to output to a file
		#f = open("/home/gary/Desktop/python/large_feed.xml",'wb')
		#f = open("/data/www/html/store/assets/xml/large_feed.xml",'wb')

	def PrettyPrint(self):
                          f = open("/home/gary/Desktop/python/large_feed.xml",'wb')
                          f.write(self._out())
                          f.close

	def Print(self):
		print(self._out().replace("\t",""))

	def TinyPrint(self):
		print(self._out().replace("\t","").replace("\n",""))

	def output(self):
		return self._out() #.replace('\t','').replace('\n','')

	def _out(self):
	    #changed tabs to spaces
		#d = u'<?xml version="1.0" encoding="UTF-8"?>\n\n'
		d = u'<?xml version="1.0" encoding="UTF-8"?>\n'
		d += ('<rss version="%s" xmlns:g="http://base.google.com/ns/1.0">\n' % self.version)
		#d += '\t<channel>\n'
		d += '  <channel>\n'
		#d += ('\t\t<title>%s</title>\n' % self.title)
		#d += ('\t\t<link>%s</link>\n' % self.link)
		#d += ('\t\t<description>%s</description>\n' % self.description)
		d += ('    <title>%s</title>\n' % self.title)
		d += ('    <link>%s</link>\n' % self.link)
		d += ('    <description>%s</description>\n' % self.description)
		#d += ('\t\t<language>%s</language>\n' % self.language)
		d += self.itemio.getvalue()
		#d += '\t</channel>\n'
		d += '  </channel>\n'
		d += '</rss>'
		return d.encode('utf-8')

#---------- End dict2rss ------------------------------------------------------------------------




#========== Functions ====================================================================================

def manufacturer(record):
    dbh = mdb.connect('localhost', 'root', '', 'solar1')
    cur = dbh.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM pseries WHERE s_id = %s" %record['p_series_id'])
    rs = cur.fetchall()
    maker_id = ""
    maker = ""
    for row in rs:
       maker_id = row['s_maker_id']

    cur.execute("SELECT * FROM maker WHERE m_id = %s" %maker_id)
    rs = cur.fetchall()
    dbh.close()
    for row in rs:
       maker = row['m_title']

    return maker


def getRecord(id, type):
    #get a single record
    #create connection to database
    dbh = mdb.connect('localhost', 'root', '', 'solar1')
    cur = dbh.cursor(mdb.cursors.DictCursor)
    if type == 'category':
       cur.execute("SELECT * FROM %s WHERE c_id = %s" %(type, id))
    else:
       cur.execute("SELECT * FROM %s WHERE s_id = %s" %(type, id))
    rs = cur.fetchall()
    dbh.close()
    return rs

def productType(pseries_id):
   rss = getRecord(pseries_id, 'pseries')
   type = ""
   category_id = ""
   for row in rss:
       series = row['s_href']
       category_id = row['s_category_id']

   rsc = getRecord(category_id, 'category')
   for row in rsc:
       type = row['c_title']

   #productList.append(type) if not in productList
   if type not in productList:
       productList.append(type)
   return type

def createLink(record):
   #function to create the link xml record
   link = "http://www.solarpanelstore.com/solar-power"
   #get the product href
   product = record['p_href']
   #get the series href
   rss = getRecord(record['p_series_id'], 'pseries')
   series = ""
   category_id = ""
   category = ""
   for row in rss:
       series = row['s_href']
       category_id = row['s_category_id']

   #get the categorys href
   rsc = getRecord(category_id, 'category')
   for row in rsc:
       category = row['c_href']

   return link + "." + category + "." + series  + "." + product + ".info.1.html"

#Handle error conditions
'''
def checkProduct(itemNo, data):
    productGood = True
    #go through data and find errors & write to dictionary
    for ???? in data:
        if ???? == 'description':
'''
           
           
           
           
           
           
           




def Raise(exception):
    #raise ValueError, exception
    raise RuntimeError(exception)

def priceCheck(price):
    if not price:
       Raise("Invalid Product Price")

    #split price to see how many zero's
    temp = str(price).split('.')
    if len(temp[1]) < 2:
       temp[1] += '0'

    return temp[0] + '.' + temp[1]

def mpnCheck(partNumber):
    #check if there is a part nummber
    if partNumber:
         #check to see if its at least 3 characters
         #Xantrex only uses 3 characters
         if len(partNumber) >= 3:
            return True
         else:
            return False
    else:
         return False

def titleCheck(data):    #NEEDS SORTING
    #check if there is a part nummber
    if data['p_man_part_num']:
       #check to see if its the title
       #if data['p_man_part_num'] == data['p_title']:
       if data['p_man_part_num'] in data['p_title'] and len(data['p_man_part_num']) == len(data['p_title']):
          #print (data['p_man_part_num'])
          #print (data['p_title'])
          #print (len(data['p_man_part_num']))
          #print (len(data['p_title']))
          return False

    if data['p_title'][0] == ".":
       #print (data['p_title'])
       return False

    return True

         #check to see if its at least 3 characters
         #Xantrex only uses 3 characters
    #     if len(partNumber) >= 3:
    #        return True
    #     else:
    #        return False
    #else:
    #     return False

def writeErrors(itemNo, error, data):

    if error == "Invalid Description":
       #try:
       problemDescription[itemNo] = {'link' : createLink(data),
                                      'title' : data['p_title'],
                                      'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                      'product_type': productType(data['p_series_id']),
                                      'description' : data['p_body'],
                                      #'brand' : manufacturer(data),
                                      'brand' : manufacturer(data)  if data['p_series_id'] else "",
                                      'adwords_grouping' : manufacturer(data),
                                      'price' : priceCheck(data['p_sale_price'])+ " USD",
                                      #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                      'shipping_weight' : str(data['p_ship_weight']) + " lb" if float(data['p_ship_weight']) > 0 else "",
                                      #'mpn' : data['p_man_part_num'],
                                      'mpn' : data['p_man_part_num'] if data['p_man_part_num'] else "",
                                      'id' : data['p_cse_part_num']
                                     }
       #except:
       #    problemData[str(itemNumber)] = {str(err): rowProduct}

    elif error == "Invalid Product Price":
        problemPrice[itemNo] = {'link' : createLink(data),
                                'title' : data['p_title'],
                                'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                'product_type': productType(data['p_series_id']),
                                'description' : data['p_body'],
                                #'brand' : manufacturer(data),
                                'brand' : manufacturer(data)  if data['p_series_id'] else "",
                                'adwords_grouping' : manufacturer(data),
                                #'price' : str(data['p_sale_price']) + " USD",
                                'price' : "",
                                #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                'shipping_weight' : str(data['p_ship_weight']) + " lb" if float(data['p_ship_weight']) > 0 else "",
                                #'mpn' : data['p_man_part_num'],
                                'mpn' : data['p_man_part_num'] if data['p_man_part_num'] else "",
                                'id' : data['p_cse_part_num']
                                }
    elif error == "Invalid Ship Weight":
        problemWeight[itemNo] = {'link' : createLink(data),
                                'title' : data['p_title'],
                                'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                'product_type': productType(data['p_series_id']),
                                'description' : data['p_body'],
                                #'brand' : manufacturer(data),
                                'brand' : manufacturer(data)  if data['p_series_id'] else "",
                                'adwords_grouping' : manufacturer(data),
                                'price' : priceCheck(data['p_sale_price'])+ " USD",
                                #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                'shipping_weight' : "",
                                #'mpn' : data['p_man_part_num'],
                                'mpn' : data['p_man_part_num'] if data['p_man_part_num'] else "",
                                'id' : data['p_cse_part_num']
                                }
    elif error == "Invalid Part Number":
        problemPartNumber[itemNo] = {'link' : createLink(data),
                                     'title' : data['p_title'],
                                     'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                     'product_type': productType(data['p_series_id']),
                                     'description' : data['p_body'],
                                     #'brand' : manufacturer(data),
                                     'brand' : manufacturer(data)  if data['p_series_id'] else "",
                                     'adwords_grouping' : manufacturer(data),
                                     'price' : priceCheck(data['p_sale_price'])+ " USD",
                                     #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                     'shipping_weight' : str(data['p_ship_weight']) + " lb" if float(data['p_ship_weight']) > 0 else "",
                                     #'mpn' : "",
                                     'mpn' : data['p_man_part_num'],
                                     'id' : data['p_cse_part_num']
                                     }
    elif error == "Invalid Manufacturer":
        problemManufacturer[itemNo] = {'link' : createLink(data),
                                     'title' : data['p_title'],
                                     'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                     'product_type': productType(data['p_series_id']),
                                     'description' : data['p_body'],
                                     'brand' : "",
                                     'adwords_grouping' : "",
                                     'price' : priceCheck(data['p_sale_price'])+ " USD",
                                     #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                     'shipping_weight' : str(data['p_ship_weight']) + " lb" if float(data['p_ship_weight']) > 0 else "",
                                     #'mpn' : data['p_man_part_num'],
                                     'mpn' : data['p_man_part_num'] if data['p_man_part_num'] else "",
                                     'id' : data['p_cse_part_num']
                                     }
    elif error == "Invalid Title":
        problemTitle[itemNo] = {'link' : createLink(data),
                                     'title' : data['p_title'],
                                     'image_link' : "http://www.solarpanelstore.com/" + data['p_imagetext'],
                                     'product_type': productType(data['p_series_id']),
                                     'description' : data['p_body'],
                                     'brand' : manufacturer(data)  if data['p_series_id'] else "",
                                     'adwords_grouping' : manufacturer(data)  if data['p_series_id'] else "",
                                     'price' : priceCheck(data['p_sale_price'])+ " USD",
                                     #'shipping_weight' : str(data['p_ship_weight']) + " lb",
                                     'shipping_weight' : str(data['p_ship_weight']) + " lb" if float(data['p_ship_weight']) > 0 else "",
                                     #'mpn' : data['p_man_part_num'],
                                     'mpn' : data['p_man_part_num'] if data['p_man_part_num'] else "",
                                     'id' : data['p_cse_part_num']
                                     }


def writeEmailBody(data):
   #print (len(problemPartNumber))

   html = ''
   for category in productList:
     writeCategory = False
     for item in data:
         if data[item]['product_type'] == category:
            if not writeCategory:
               writeCategory = True
               html += '<tr>\n'
               html += '<td colspan="2" style="text-align:center;font-weight: bold;padding:10px 0px 20px 0px;">%s</td>\n' %category
               html += '</tr>\n'

            #Function to write table contents section of html email
            html += '<tr>\n'
            html += '<td colspan="2" style="vertical-align:center;"><h2>%s</h2></td>\n' %data[item]['title']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td colspan="2"><h3>Item&#39;s URL: <a href="%s">%s</a></h3></td>\n' %(data[item]['link'],data[item]['link'])
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td colspan="2" class="product"><h3>Product Details</h3></td>\n'
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td colspan="2" class="database"><h3>Database Information</h3></td>\n'
            html += '</tr>\n'
            html += '<tr>\n'
            #htmlcode += '<div style="-moz-column-count: 2;-moz-column-gap: 0.2em;-webkit-column-count: 2;-webkit-column-gap: 0.2em;"><dl><dt style="float:left;width:100px;">id:</dt>'
            html += '<td class="sub_title">id:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['id']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">description:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['description'].decode('ascii', 'ignore')   #[0:150]
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">adword grouping:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['adwords_grouping']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">type:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['product_type']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">brand:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['brand']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">manufacturer part number:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['mpn']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">price:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['price']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td class="sub_title">shipping weight:</td>\n'
            html += '<td class="details">%s</td>\n' %data[item]['shipping_weight']
            html += '</tr>\n'
            html += '<tr>\n'
            html += '<td height="25px">&nbsp;</td>\n'
            html += '<td >&nbsp;</td>\n'
            html += '</tr>\n'

   return html

def writeEmailHead():
    #Function to write head section of html email
    html = '<!DOCTYPE html>\n'
    #try and build the email
    html += '<html>\n<head>\n'
    html += '\t<style type="text/css">\n'
    html += '\t\tbody {\n'
    #htmlcode += background-color: #7f8092;
    html += '\t\t\tfont-size: 62.5%;\n'
    html += '\t\t\tfont-family: Verdana, Arial, SunSans-Regular, Sans-Serif;\n'
    #htmlcode += padding:0px;
    #htmlcode += margin:0px;
    html += '\t\t}\n'
    html += '\t\t.head-error {\n'
    #htmlcode += '\t\t\tfont-size: 0.9em;\n'
    #htmlcode += '\t\t\theight: 30px;\n'
    #htmlcode += '\t\t\tvertical-align:center;\n'
    #htmlcode += '\t\t\tfloat: left;\n'
    html += '\t\t\tpadding-left: 13%;\n'
    #htmlcode += '\t\t\tmargin:0px;\n'
    #htmlcode += '\t\t\tbackground-color: #7D848D;\n'
    #htmlcode += '\t\t\ttext-align: center;\n'
    html += '\t\t}\n'

    html += '\t\th2 {\n'
    html += '\t\t\tfont-size: 0.9em;\n'
    html += '\t\t\theight: 30px;\n'
    #htmlcode += '\t\t\tvertical-align:center;\n'
    html += '\t\t\tcolor: white;\n'
    html += '\t\t\tpadding:0px 0px 0px 2px;\n'
    html += '\t\t\tmargin:0px;\n'
    html += '\t\t\vertical-align:center;\n'
    html += '\t\t\tbackground-color: #7D848D;\n'
    html += '\t\t}\n'
    html += '\t\th3 {\n'
    html += '\t\t\tfont-size: 0.75em;\n'
    html += '\t\t\tpadding:0px 0px 0px 10px;\n'
    html += '\t\t\tmargin:0px;\n'
    html += '\t\t}\n'
    #htmlcode += '\t\ttable {\n'
    #htmlcode += '\t\t\tfont-size: 1em;\n'
    #htmlcode += '\t\t\tpadding:0px 0px 0px 0px;\n'
    #htmlcode += '\t\t\tmargin:0px;\n'
    #htmlcode += '\t\t}\n'
    html += '\t\t.product {\n'
    html += '\t\t\tpadding:20px 0px 10px 0px;\n'
    html += '\t\t}\n'
    html += '\t\t.database {\n'
    html += '\t\t\tpadding:0px 0px 0px 0px;\n'
    #htmlcode += '\t\t\tfont-size: 0.75em;\n'
    html += '\t\t\tfont-weight: bold;\n'
    html += '\t\t\theight: 20px;\n'
    #htmlcode += '\t\t\twidth: 100px;\n'
    #htmlcode += '\t\t\tvertical-align:top;\n'
    #htmlcode += '\t\t\tmargin-left:5px;\n'
    html += '\t\t\tbackground-color: #D0DCEB;\n'
    html += '\t\t}\n'

    html += '\t\t.sub_title {\n'
    html += '\t\t\tpadding:0px 0px 0px 20px;\n'
    html += '\t\t\tfont-size: 0.75em;\n'
    html += '\t\t\tfont-weight: bold;\n'
    html += '\t\t\twidth: 200px;\n'
    html += '\t\t\tvertical-align:top;\n'
    #htmlcode += '\t\t\tbackground-color: #D0DCEB;\n'
    html += '\t\t}\n'
    html += '\t\t.details {\n'
    html += '\t\t\tpadding:0px 0px 0px 0px;\n'
    html += '\t\t\tfont-size: 0.75em;\n'
    html += '\t\t}\n'
    html += '\t\t.header {\n'
    html += '\t\t\tpadding:0px 0px 0px 0px;\n'
    html += '\t\t\tfont-size: 1.25em;\n'
    html += '\t\t\ttext-align: center;\n'
    html += '\t\t}\n'
    html += '\t\t.header ul {\n'
    html += '\t\t\tlist-style-type: none;\n'
    html += '\t\t}\n'
    html += '\t\t.invalid {\n'
    html += '\t\t\tpadding:10px 0px 10px 0px;\n'
    html += '\t\t\tfont-size: 1.0em;\n'
    html += '\t\t\tpadding-left: 20%;\n'
    html += '\t\t}\n'
    html += '\t\t.invalid-note {\n'
    html += '\t\t\tpadding:10px 0px 10px 0px;\n'
    html += '\t\t\tfont-size: 1.25em;\n'
    html += '\t\t\tpadding-left: 13%;\n'
    html += '\t\t}\n'

    html += '\t</style>\n'
    html += '</head>\n<body>\n'
    return html
#need a function to sanitize the description

#========== Main =========================================================================================

#get all the categories with status of 1 (active)
dbh = mdb.connect('localhost', 'root', '', 'solar1')
#query the database into a dictionary
cur = dbh.cursor(mdb.cursors.DictCursor)
cur.execute("SELECT * FROM category WHERE c_status = '1'")
rsCategory = cur.fetchall()
dbh.close()
#setup the dictionaries and other base variables
feedData = {}
problemData = {}
problemDescription = {}
problemWeight = {}
problemPrice = {}
problemPartNumber = {}
problemManufacturer = {}
problemTitle = {}
productList = []
errorList = {'price': problemPrice,
             'mpn' : problemPartNumber,
             'brand' : problemManufacturer,
             'title' : problemTitle,
             'shipping_weight' : problemWeight
            }

itemNumber = 1
itemData = {}

#make sure we have something returned
if len(rsCategory) > 0:
    for rowCategory in rsCategory:
        dbh = mdb.connect('localhost', 'root', '', 'solar1')
        cur = dbh.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM pseries WHERE s_category_id = %s AND s_status = '1'" %rowCategory['c_id'])
        rsSeries = cur.fetchall()
        dbh.close()
        #print (rsSeries)
        #exit(0)
        #make sure we have something returned
        if len(rsSeries) > 0:
           #itemNumber = 1
           #itemData = {}
           for rowSeries in rsSeries:
               #get the active products
               dbh = mdb.connect('localhost', 'root', '', 'solar1')
               cur = dbh.cursor(mdb.cursors.DictCursor)
               cur.execute("SELECT * FROM product WHERE p_series_id = %s AND p_status = '1'" %rowSeries['s_id'])
               rsProduct = cur.fetchall()
               dbh.close()
               #make sure we have something returned
               #print rs_product
               if len(rsProduct) > 0:
                  #cycle through the product series
                  for rowProduct in rsProduct:
                      if int(rowProduct['p_in_stock_count']) > 0:
                         availability = "in stock"
                      else:
                         availability = "available for order"

                      if rowCategory['c_id'] == "37":
                         googleProductCategory = "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Energy Kits"
                      elif rowCategory['c_id'] == "1" or "2" or "33" or "35":
                         googleProductCategory = "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Panels"
                      else:
                         googleProductCategory = "Hardware &gt; Renewable Energy &gt; Solar Energy"

                      if not rowProduct['p_cse_part_num'] == 'COLO-00737':       #hard exclude "PV Array Design"
                          try:
                              itemData[str(itemNumber)]= {
                                                         'description' : rowProduct['p_body'].decode('ascii'),
                                                         #'g:mpn' : rowProduct['p_man_part_num'] if rowProduct['p_man_part_num'] >= 6) else Raise("Invalid Part Number"),
                                                         #'g:mpn' : rowProduct['p_man_part_num'] if ( len(rowProduct['p_man_part_num']) >= 6 or rowProduct['p_man_part_num']) else Raise("Invalid Part Number"),
                                                         'g:mpn' : rowProduct['p_man_part_num'] if mpnCheck(rowProduct['p_man_part_num']) else Raise("Invalid Part Number"),
                                                         'g:brand' : manufacturer(rowProduct)  if rowProduct['p_series_id'] else Raise("Invalid Manufacturer"),
                                                         'g:price' : priceCheck(rowProduct['p_sale_price'])+ " USD",
                                                         'g:shipping_weight' : str(rowProduct['p_ship_weight']) + " lb" if float(rowProduct['p_ship_weight']) > 0 else Raise("Invalid Ship Weight"),
                                                         #'title' : rowProduct['p_title'] if not rowProduct['p_man_part_num'] in rowProduct['p_man_part_num'] else Raise("Invalid Title"),
                                                         
                                                         #NEEDS SORTING
                                                         #'title' : rowProduct['p_title'],
                                                         'title' : rowProduct['p_title'] if titleCheck(rowProduct) else Raise("Invalid Title"),

                                                         'link' : createLink(rowProduct),
                                                         #Try & decode text, will error for odd characters
                                                         'g:id' : '%s-CS' %rowProduct['p_cse_part_num'],
                                                         'g:condition' : "new",
                                                         #'g:price' : str(rowProduct['p_sale_price']) + " USD" if rowProduct['p_sale_price'] else Raise("Invalid Product Price"),
                                                         'g:availability' : availability,
                                                         'g:image_link' : "http://www.solarpanelstore.com/" + rowProduct['p_imagetext'],
                                                         'g:adwords_grouping' : manufacturer(rowProduct),
                                                         'g:google_product_category' : googleProductCategory,
                                                         'g:product_type': productType(rowProduct['p_series_id'])}

                          except UnicodeDecodeError:
                              #handle illegal characters in description
                              problemData[str(itemNumber)] = {"Invalid Description": rowProduct}

                          except RuntimeError, err:
                              #handle other errors
                              problemData[str(itemNumber)] = {str(err): rowProduct}

                          itemNumber += 1

    #create xml file
    feedData['item'] = itemData
    d = dict2rss(feedData)
    d.PrettyPrint()

    #sort list
    productList = sorted(productList)

    #print(productList)
    #exit(0)
    #check for errors and email
    if len(problemData) > 0:
        #get the errors and sort
        #print (problemData)
        #exit(0)
        for itemNo in problemData:
            for error in problemData[itemNo]:
               if error == "Invalid Description":
                  writeErrors(itemNo, "Invalid Description", problemData[itemNo][error])
               elif error == "Invalid Product Price":
                  writeErrors(itemNo, "Invalid Product Price", problemData[itemNo][error])
               elif error == "Invalid Ship Weight":
                  writeErrors(itemNo, "Invalid Ship Weight", problemData[itemNo][error])
               elif error == "Invalid Part Number":
                  writeErrors(itemNo, "Invalid Part Number", problemData[itemNo][error])
               elif error == "Invalid Manufacturer":
                  writeErrors(itemNo, "Invalid Manufacturer", problemData[itemNo][error])
               elif error == "Invalid Title":
                  writeErrors(itemNo, "Invalid Title", problemData[itemNo][error])


        #need to look through each set of errors and see if there are others
        for itemNo in problemDescription:
            for key, value in problemDescription[itemNo].iteritems():
                if key != 'description':
                    if value == '':
                       for x in errorList:
                           if x == key:
                              errorList[key][itemNo] = problemDescription[itemNo]

        for itemNo in problemPrice:
            for key, value in problemPrice[itemNo].iteritems():
               if not (key == 'description' or key == 'price'):
                    if value == '':
                       for x in errorList:
                           if x == key:
                              errorList[key][itemNo] = problemPrice[itemNo]

        for itemNo in problemPartNumber:
            for key, value in problemPartNumber[itemNo].iteritems():
                if not (key == 'description' or key == 'price' or key == 'mpn'):
                    if value == '':
                       for x in errorList:
                           if x == key:
                              errorList[key][itemNo] = problemPartNumber[itemNo]

        for itemNo in problemManufacturer:
            for key, value in problemManufacturer[itemNo].iteritems():
                if not (key == 'description' or key == 'price' or key == 'mpn' or key == 'brand'):
                    if value == '':
                       for x in errorList:
                           if x == key:
                              errorList[key][itemNo] = problemManufacturer[itemNo]

        #need to add shipping.


        #setup email
        sender = 'noreply@cosolar.com'
        receivers = ['gary@cosolar.com']
        #receivers = ['gary@cosolar.com', 'ericw@cosolar.com']
        #ccers = ['gary@burningmtn.com']
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "GMS xml file Generation Errors"
        msg['From'] = sender
        #msg['To'] = receivers
        msg['To'] = COMMASPACE.join(receivers)
        #msg['Cc'] = COMMASPACE.join(ccers)

        #create html email
        htmlcode = writeEmailHead()

        htmlcode += '<div class="header">'
        htmlcode += '<p>Products listed below have not been included in the Google Merchant Center.  Errors are categorized into the following, a product may fall into one or more of these areas.</p>'
        htmlcode += '<ul>'
        htmlcode += '<li>Product Description</li>'
        htmlcode += '<li>Manufacturer / Vendor</li>'
        htmlcode += '<li>Product Price</li>'
        #htmlcode += '<li>Shipping Weight</li>'
        #htmlcode += '<li><a href="#ship_weight">Shipping Weight</a></li>'
        #htmlcode += '<li><a href="#part_number">Manufactures part number</a></li>'
        htmlcode += '<li>Manufactures Part Number</li>'
        htmlcode += '<li>Product Shipping Weight</li>'
        htmlcode += '</ul>'
        htmlcode += '</div>'
        #write table for each error
        if len(problemDescription) > 0:
          htmlcode += '<a name="description"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Product Description</h1></p>'
          htmlcode += '<p>%s product description error(s) found</p>' %len(problemDescription)
          htmlcode += '</div>'
          htmlcode += '<div class="invalid-note">'
          htmlcode += 'Note: Product description errors are normally due to invalid characters, examples of which are:<br>'
          htmlcode += '<div class="invalid">'
          htmlcode += '&acirc;&euro;&#8482;<br>'
          htmlcode += '&#194;<br>'
          htmlcode += '&acirc;&euro;<br>'
          htmlcode += '&acirc;&euro;&#8220;<br>'
          htmlcode += '&acirc;&euro;&#8221;<br>'
          htmlcode += '&#226;&#8222;&#162;<br>'
          htmlcode += '&acirc;&euro;&#126;<br>'
          htmlcode += '</div>'
          htmlcode += 'This usually occurrs when a description is <em>cut & pasted</em> from a vendors web site, though the page on the local store looks correct, the public site will display the invalid characters.'
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemDescription)
          htmlcode += '</table>\n'

        if len(problemManufacturer) > 0:
          htmlcode += '<a name="ship_weight"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Manufacturer</h1></p>'
          htmlcode += '<p>%s manufacturer error(s) found</p>' %len(problemManufacturer)
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemManufacturer)
          htmlcode += '</table>\n'

        if len(problemPrice) > 0:
          htmlcode += '<a name="price"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Product Price</h1></p>'
          htmlcode += '<p>%s product price error(s) found</p>' %len(problemPrice)
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemPrice)
          htmlcode += '</table>\n'

        if len(problemPartNumber) > 0:
          htmlcode += '<a name="part_number"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Manufacturer Part Number</h1></p>'
          htmlcode += '<p>%s manufacturer part number error(s) found</p>' %len(problemPartNumber)
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemPartNumber)
          htmlcode += '</table>\n'

        if len(problemWeight) > 0:
          htmlcode += '<a name="ship_weight"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Shipping Weight</h1></p>'
          htmlcode += '<p>%s shipping weight error(s) found</p>' %len(problemWeight)
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemWeight)
          htmlcode += '</table>\n'

        if len(problemTitle) > 0:
          htmlcode += '<a name="ship_weight"></a>'
          htmlcode += '<div class="head-error">'
          htmlcode += '<p><h1>Title</h1></p>'
          htmlcode += '<p>%s title error(s) found</p>' %len(problemWeight)
          htmlcode += '</div>\n'
          htmlcode += '<table border="0" width="75%" align="center">\n'
          htmlcode += writeEmailBody(problemTitle)
          htmlcode += '</table>\n'

        #htmlcode += '</table>\n'
        htmlcode += '</body>\n</html>\n'

        body = MIMEText(htmlcode, 'html')
        msg.attach(body)

        #send email
        #try:
        smtpObj = smtplib.SMTP('localhost')
        #smtpObj.sendmail(sender, receivers, message)
        #smtpObj.sendmail(sender, receivers + ccers, msg.as_string())
        smtpObj.sendmail(sender, receivers, msg.as_string())
        #print (message)
        #print ("Successfully sent email")
        #except SMTPException:
        #    print ("Error: unable to send email")


else:
    print ("Fatal Error")


