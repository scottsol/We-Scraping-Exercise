"""
Your task is to write a python program to do the following:
    1) For each inspection for each facility on a single page of results from the Napa county health
       department website (url given below), scrape the following information:
       - Facility name
       - Address (just street info, not city, state, or zip)
       - City
       - State
       - Zipcode
       - Inspection date
       - Inspection type
       - For each out-of-compliance violation type, scrape the violation type number and corresponding description.
         For example, an inspection might contain violation type numbers 6 and 7, and descriptions
         "Adequate handwashing facilities supplied & accessible" and "Proper hot and cold holding temperatures"
    2) Place this information in a database of some sort. You can use whatever you want; sqlite, postgres, mongodb, etc.
       Organize the data in a fashion which seems the most logical and useful to you. Include in your result the
       necessary instructions to set up this database, such as create table statements.
    3) Fetch this information from the database, and print it to the console in some fashion which clearly
       and easily displays the data you scraped.

We have provided a little bit of code using the lxml and sqlite to get you started,
but feel free to use whatever method you would like.
"""


import sqlite3
import requests
import re
import pprint # used to debug and verify data
from bs4 import BeautifulSoup
from lxml import html
from lxml.html import tostring



page_url = (
    "http://ca.healthinspections.us/napa/search.cfm?start=1&1=1&sd=01/01/1970&ed=03/01/2017&kw1=&kw2=&kw3="
    "&rel1=N.permitName&rel2=N.permitName&rel3=N.permitName&zc=&dtRng=YES&pre=similar"
)

# function to create a table
def setup_db():
    conn = sqlite3.connect("exercise.db")
    c = conn.cursor()
    createTable = """CREATE TABLE IF NOT EXISTS napaCounty(
                  facility_name TEXT,
                  address TEXT,
                  city TEXT,
                  state VARCHAR(2),
                  zip_code varchar(5),
                  inspection_date DATE,
                  inspection_grade TEXT
                  );"""
    c.execute(createTable)
    c.close()

# function to insert dictionary data
def insert_db(dict):
  conn = sqlite3.connect("exercise.db")
  c = conn.cursor()

  for x in range (0, 10):
    c.execute("INSERT INTO napaCounty (facility_name, address, city, state, zip_code, inspection_date, inspection_grade) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (dict[x]['name'], dict[x]['address'], dict[x]['city'], dict[x]['state'], dict[x]['zip'], dict[x]['i_date'], dict[x]['i_grade']))
  
  conn.commit()
  c.close()
  conn.close()

# function to read from the database
def read_from_db():
  conn = sqlite3.connect("exercise.db")
  c = conn.cursor()
  c.execute('SELECT * FROM napaCounty')
  data = c.fetchall()
  pprint.pprint(data)

# read from a single page of the county data and return a dictionary of the data 
def scrape():
  r = requests.get(page_url)
  soup = BeautifulSoup(r.text,"lxml")
  dictionary = {}
  


  facility_name = soup.find_all("b")
  address = soup.find_all('div', style = re.compile('margin-bottom:10px'))
  for x in range (0,10):
    facName = facility_name[1 + 2 * x].text
    
    addressCluster = address[x].text
    addressLines = addressCluster.splitlines()
 

    line1 = addressLines[1].strip()
    line2 = addressLines[2].strip()
    zipCode = line2[-5:] #trim zipcode as last 5 characters
    
    line2 = line2[:-6] #remove zipcode
    
    state = line2[-2:] #trim state as last 2 characters
    
    city = line2[:-4] # trim state

    inspection_date = addressLines[4].strip()[22:]
    
    inspection_grade = addressLines[8].strip()
    
    dictionary[x] = {
    'name': facName,
    'address' : line1,
    'city' : city,
    'state' : state,
    'zip' : zipCode,
    'i_date' : inspection_date,
    'i_grade': inspection_grade
    }

  return dictionary



def main():
    setup_db()
    dict = scrape()
    insert_db(dict)
    read_from_db()

    

if __name__ == '__main__':
    main()

