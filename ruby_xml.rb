require 'rubygems'

require 'builder'
require 'mysql'
require 'sanitize'

def getSeriesRecord(id)
    #get a single record
    #create connection to database
    dbh = Mysql.new 'localhost', 'root','', 'solar1'
    rs = dbh.query("SELECT * FROM pseries WHERE s_id = " + id)
    dbh.close if dbh
    return rs
end

def getCategoryRecord(id)
    #get a single record
    #create connection to database
    dbh = Mysql.new 'localhost', 'root','', 'solar1'
    rs = dbh.query("SELECT * FROM category WHERE c_id = " + id)
    dbh.close if dbh
    return rs
end

def productType(pseries_id)
   rss = getSeriesRecord(pseries_id)
   type = ""
   category_id = ""
   rss.each_hash do |row|
       series = row['s_href']
       category_id = row['s_category_id']
   end
   rsc = getCategoryRecord(category_id)
   rsc.each_hash do |row|
       type = row['c_title']
   end

   return type
end

def createLink(record)
   #function to create the link xml record
   link = "http://www.solarpanelstore.com/solar-power"
   #get the product href
   product = record['p_href']
   #get the series href
   rss = getSeriesRecord(record['p_series_id'])
   series = ""
   category_id = ""
   category = ""
   rss.each_hash do |row|
       series = row['s_href']
       category_id = row['s_category_id']
   end
   #get the categorys href
   rsc = getCategoryRecord(category_id)
   rsc.each_hash do |row|
       category = row['c_href']
   end
   return link + "." + category + "." + series  + "." + product + ".info.1.html"
end

def manufacturer(record)
   dbh = Mysql.new 'localhost', 'root','', 'solar1'
   rs = dbh.query("SELECT * FROM pseries WHERE s_id = " + record['p_series_id'])
   maker_id = ""
   maker = ""
   rs.each_hash do |row|
       maker_id = row['s_maker_id']
   end
   rs = dbh.query("SELECT * FROM maker WHERE m_id = " + maker_id)
   dbh.close if dbh
   rs.each_hash do |row|
       maker = row['m_title']
   end

    return maker
end

def parseDescription(description)
    #find 1st <br>
    pos = description.index('<br>')
#   remove ’ from any text
#    puts description
    if pos.nil?
        paragraph = description
    else
        paragraph = description.slice(0..pos - 1)
    end

#    paragraph = description.to_s.split('<br>')

    #test of sanitize
    html = paragraph
    puts html
    clean_html = Sanitize.clean(html)
#    puts paragraph
    puts "-----------------------------------"
#    puts clean_html


    return paragraph.strip
end

def createXML(product, filename)

    #check out the product hash first and look for issues
    item.each_key {|key|
        #check for shipping weight
        if row_product['p_ship_weight'].empty?
           #write to file or something to note issue
           return false
        elsif row_product['p_man_part_num'].empty?
           #write to file or something to note issue
           return false
        end

        puts item[key]['title']
        puts item[key]['link']
    }
    return true
end


#get product records from database

=begin
#create connection to database
dbh = Mysql.new 'localhost', 'root','', 'solar1'
#query the database pulling only Magnum Inverters
rs = dbh.query("SELECT * FROM product WHERE p_series_id = '123' AND p_status = '1'")
dbh.close if dbh

#create xml file

#path for file location is /data/www/html/store/assets/xml/
file = File.new("inverter_feed.xml", "w")
#create xml header information
#xml = Builder::XmlMarkup.new( :target => $stdout, :indent => 2 )
xml = Builder::XmlMarkup.new( :target => file, :indent => 2 )
xml.instruct! :xml, :version => "1.0"
xml.rss("version" => "2.0", "xmlns:g" => "http://base.google.com/ns/1.0") {
    xml.channel {
        xml.title("Inverter Feed")
	    xml.link("http://www.solarpanelstore.com")
	    xml.description("Everything you need to go Solar")

        #create each item from the recordset
        rs.each_hash do |row|
            #check that there is a shipping weight if not don't write
            if !row['p_ship_weight'].empty?
                xml.item {
                    xml.title(row['p_title'])
		            xml.link(createLink(row))
                    xml.description(parseDescription(row['p_body']))
                    xml.g :id, row['p_cse_part_num']
		            xml.g :condition, "new"
                    xml.g :price, row['p_sale_price'] + " USD"
		            if row['p_in_stock_count'].to_i > 0
                       xml.g :availability, "in stock"
                    else
                       xml.g :availability, "available for order"
                    end
		            xml.g :image_link, "http://www.solarpanelstore.com/" + row['p_imagetext']
                    xml.g :mpn, row['p_man_part_num']
                    xml.g :brand, manufacturer(row)
		            xml.g :google_product_category, "Hardware &gt; Renewable Energy &gt; Solar Energy"
                    xml.g :shipping_weight, row['p_ship_weight'] + " lb"
		            #xml.g :product_type, "Magnum Inverters"
		            xml.g :product_type, productType(row['p_series_id'])
   	            }

   	        end
        end
    }
}

#close xml file
file.close

=end

#get all the categories with status of 1
dbh = Mysql.new 'localhost', 'root','', 'solar1'
#query the database pulling only Magnum Inverters
rs_cat = dbh.query("SELECT * FROM category WHERE c_status = '1'")
dbh.close if dbh

#make sure we have something returned
if rs_cat.num_rows > 0
    #cycle through the active categories
    rs_cat.each_hash do |row_cat|
    
    if row_cat['c_id'] == "37"
        google_product_category = "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Energy Kits"
    elsif row_cat['c_id'] == "1" || row_cat['c_id'] == "2" || row_cat['c_id'] == "33" || row_cat['c_id'] == "35"
        google_product_category = "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Panels"
    else
        google_product_category = "Hardware &gt; Renewable Energy &gt; Solar Energy"
    end


        #create the xml file name
        xml_file_name = "/home/gary/Desktop/ruby/xml_files/" + row_cat['c_href'] + ".xml"
        #puts xml_file_name
        xml_file = File.new(xml_file_name, "w")
        xml = Builder::XmlMarkup.new( :target => xml_file, :indent => 2 )
        xml.instruct! :xml, :version => "1.0"
        #create xml header information
        xml.rss("version" => "2.0", "xmlns:g" => "http://base.google.com/ns/1.0") {
            xml.channel {
                xml.title(row_cat['c_title'])
	            xml.link("http://www.solarpanelstore.com")
	            xml.description("Everything you need to go Solar")
                #get the active product series id's associated with the category
                dbh = Mysql.new 'localhost', 'root','', 'solar1'
                rs_series = dbh.query("SELECT * FROM pseries WHERE s_category_id = " + row_cat['c_id']  + " AND s_status = '1'")
                dbh.close if dbh

                #make sure we have something returned
                if rs_series.num_rows > 0

                    #cycle through the product series
                    rs_series.each_hash do |row_series|
                        #get the active products
                        dbh = Mysql.new 'localhost', 'root','', 'solar1'
                        rs_product = dbh.query("SELECT * FROM product WHERE p_series_id = " + row_series['s_id'] + " AND p_status = '1'")
                        dbh.close if dbh

                        #make sure we have something returned
                        if rs_product.num_rows > 0
                            item_number = 1
                            item = Hash.new
                            #cycle through the product series
                            rs_product.each_hash do |row_product|
                                #puts row_product['p_cse_part_num']


                                item_key = "Item" + item_number.to_s
                                item = { item_key => {
                                                      'title' => row_product['p_title'],
                                                      'link' => createLink(row_product),
                                                      'description' => row_product['p_body'],
                                                      'id' => row_product['p_cse_part_num'],
                                                      'condition' => "new",
                                                      'price' => row_product['p_sale_price'] + " USD",
                                                      'availability' => row_product['p_in_stock_count'],
                                                      'image_link' => "http://www.solarpanelstore.com/" + row_product['p_imagetext'],
                                                      'mpn' => row_product['p_man_part_num'],
                                                      'brand' => manufacturer(row_product),
                                                      'google_product_category' => google_product_category,
                                                      'shipping_weight' => row_product['p_ship_weight'] + " lb",
                                                      'product_type' => productType(row_product['p_series_id'])
                                                      }
                                        }
                                #keys = item.keys
                                #puts item[item_key]['title']

=begin
                                if !row_product['p_ship_weight'].empty? || !row_product['p_man_part_num'].empty?

                                    xml.item {
                                        xml.comment("Item Number:- " + item_number.to_s)
                                        xml.title(row_product['p_title'])
                    		            xml.link(createLink(row_product))
                                        xml.description(parseDescription(row_product['p_body']))
                                        xml.g :id, row_product['p_cse_part_num']
                    		            xml.g :condition, "new"
                                        xml.g :price, row_product['p_sale_price'] + " USD"
                    		            if row_product['p_in_stock_count'].to_i > 0
                                           xml.g :availability, "in stock"
                                        else
                                           xml.g :availability, "available for order"
                                        end
                    		            xml.g :image_link, "http://www.solarpanelstore.com/" + row_product['p_imagetext']
                                        xml.g :mpn, row_product['p_man_part_num']
                                        xml.g :brand, manufacturer(row_product)

                                        if row_cat['c_id'] == "37"
                                            xml.g :google_product_category, "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Energy Kits"
                                        elsif row_cat['c_id'] == "1" || row_cat['c_id'] == "2" || row_cat['c_id'] == "33" || row_cat['c_id'] == "35"
                                            xml.g :google_product_category, "Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Panels"
                                        else
                                            xml.g :google_product_category, "Hardware &gt; Renewable Energy &gt; Solar Energy"
                                        end
                                        #xml.g :google_product_category, "Hardware &gt; Renewable Energy &gt; Solar Energy"
                                        #need to get the next 2 lines used
                    		            #Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Panels
                    		            #Hardware &gt; Renewable Energy &gt; Solar Energy &gt; Solar Energy Kits

                                        xml.g :shipping_weight, row_product['p_ship_weight'] + " lb"
                    		            #xml.g :product_type, "Magnum Inverters"
                    		            xml.g :product_type, productType(row_product['p_series_id'])
                       	            }
                                    item_number = item_number + 1
                       	        end
=end
                                item_number = item_number + 1
                            end
                            item.each_key {|key|
                                puts item[key]['title']
                                puts item[key]['link']
                                }
                        end
                    end
                end
            }
        }
        #close xml file
        xml_file.close
    end
end