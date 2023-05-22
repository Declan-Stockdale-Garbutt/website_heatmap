# Base imports
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import os
#import time
import datetime

# wayback machine 
from waybackpy import WaybackMachineSaveAPI
from waybackpy import WaybackMachineCDXServerAPI

from collections import OrderedDict

import warnings
warnings.filterwarnings('ignore')


# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def scrape_website(url):
    
    # Get page data
    page = requests.get(url)

    # Parse it
    soup = BeautifulSoup(page.content, "html.parser")
    
    # Convert to string
    soup_str = str(soup)
    
    return soup_str

def scrape_website_selenium(url):
    # Configure Selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    # Navigate to website and wait for page to fully load
    driver.get(url)
    
    print('waiting')
    wait = WebDriverWait(driver, 1)
    print('finished waiting')
    
    
    wait.until(EC.presence_of_element_located((By.XPATH, "//html/body")))
    print('found element')

    # Get page source
    soup_str = driver.page_source

    # Quit driver
    driver.quit()

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(soup_str, "html.parser")

    return str(soup)


def carousel(all_splits,website):
        
    # Carousel has no label and needs it own logic to find urls
    
    if website.lower() == 'sports' or website.lower() == 'sport':
        break_condition = 'data-layer-event-source-title="Sport in focus"'
    
    elif website.lower() == 'news':
        break_condition = 'data-layer-event-source-title="Just In"'

    
    # carousel
    carousel_items = []

    # loop over all splits (div and section)
    for i, item in enumerate(all_splits):
        
        # convert to string
        item = str(item)

        # find carousel at top
        carousel_items.append(item)
        
        # Break if Just in, this is first title of section below carousel
        if break_condition in item:
            break

    # create empty list
    carousel_urls = []
    
    # loop over splits within carousel
    for thing in carousel_items:

        # Filter out non url containing splits
        if 'www.sbs.com.au/' in thing and '/tag/' not in thing and 'rel="noopener noreferrer" target="_blank' not in thing and 'style="text-decoration:none' not in thing:

            # parse to find url
            url = thing[thing.find('www.sbs.com.au'):]
            url = url[:url.find('">')]
            carousel_urls.append(url)

    # remove duplicates - mainly tags and links to images that match base url of main articles e.g. base -> article image->article/img
    carousel_urls = list(set(carousel_urls))   
    
    # put into list format which is easier to join with rest of news output
    carousel_urls_output = []
    for url in carousel_urls:
        carousel_urls_output.append(['Carousel',url])
        
    # need i to know where to start the rest of news function and not repeat carousel results
    return carousel_urls_output, i


def rest_of_page(all_splits, i):
    
    # Get urls from the rest of the sections within a historic SBS website
    
    # empty list
    heading_url_initial = []
    
    # loop over splits using i which is the starting value from carousel function
    for i, item in enumerate(all_splits[i:]):
        
        # convert to string
        item = str(item)
        
        # only care about relevant url and split containing section heading
        if 'sbs.com.au' in item or 'data-layer-event-source-title="' in item:

            # Parse section heading
            if 'data-layer-event-source-title=' in item:
                section_name = item[item.find('data-layer-event-source-title="')+len('data-layer-event-source-title="'):]
                section_name = section_name[:section_name.find('"')]

            # Parse Url
            if 'sbs.com.au' in item:
                
                
                # get url
                url = item[item.rfind('href=')+len('href='):item.rfind('"')]              
                
                url = url[url.find('http'):]
                
                # This causing issues
                if '>' in url:
                    url = url[:url.find('>')]

                # fix edge cases
                url = url.replace(' tabindex="',"")
                url = url.replace(' target="_blank"',"")
                url = url.replace(' target="_blan',"")


                if 'images.sbs.com.au' in url or len(url) < 10 or 'rel="noopener noreferrer"' in url or 'svg' in url:
                    continue

                
                # Same format as carousel
                heading_url_initial.append([section_name,url])
                
    return heading_url_initial

def convert_to_dict(list1,list2):
    
    # combine lists
    all_results = list1+list2
    
    # output as dict
    result = {}

    # loop over lists output is {'Heading':Urls} e.g. {"Carousel": [url1, url2], "Heading 2", [url1, url2]}
    for d in all_results:
        if d[0] in result:
            result[d[0]].append(d[1])
        else:
            result[d[0]] = [d[1]]
            
    return result

def parse_website(website_string, url, website_type, date):
    
    url = str(url)
    website_type = str(website_type)

    # start from main using wayback machine
    test_output = website_string[website_string.find('<main'):]

    # split into divs
    init_splits = test_output.split('div class="MuiBox-root css')

    # some divs contains sections which themselves are pseudo divs, need to split again
    all_splits = []
    
    # loop over splits
    for item in init_splits:

        if 'section class=' in item:
            pass

        final_split = item.split('section class=')
        all_splits.append(final_split)


    # Website type (sport or news) - required to find break condition for first div thats not the carousel
    
    # Get carousel info and when carousel ends
    carousel_results,i = carousel(all_splits,website_type)
    
    # Get rest of results
    rest_of_page_results = rest_of_page(all_splits,i)
    
    # convert both lists above into one dictionary
    dictionary_results = convert_to_dict(carousel_results, rest_of_page_results)
    
    dictionary_results_final = {'Date'    : date,
                                'Website' : url,
                                'Results' : dictionary_results}
    
    return dictionary_results_final

def get_snapshots(url, start_timestamp, end_timestamp):

    # Get historic snapshots form wayback machine
    
    
    # Header info 
    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    save_api.save()
    
    # timestamp is year month day
    cdx = WaybackMachineCDXServerAPI(url, user_agent, start_timestamp=20221201, end_timestamp=20230302)
    
    # list all snapshots
    list_snapshots = [item.archive_url for item in cdx.snapshots()]
    
    # Some days have multiple snapshots, only want latest for each day
    latest_daily = []

    # Compare snapshot dates in loop
    for i in range(0,len(list_snapshots)-1):

        # Characters 28:26 are the year month day. Check that item below doesn't have same value
        if list_snapshots[i][28:36] == list_snapshots[i+1][28:36]:
            continue
        else:
            latest_daily.append(list_snapshots[i])
            
    return latest_daily

def fix_just_in(result):

    result['Results']['Top Stories'] = result['Results']['Just In'][-4:]
    result['Results']['Just In'] = result['Results']['Just In'][:-4]


    # Make a copy of the dictionary before modifying it
    results_copy = result['Results'].copy()


    # Remove the 'Top Stories' key from the copy
    top_stories_value = results_copy.pop('Top Stories')

    # Insert the 'Top Stories' key at the desired index
    new_order = list(results_copy.keys())
    new_order.insert(2, 'Top Stories')

    # Create a new ordered dictionary with the desired order of keys
    new_dict = OrderedDict((key, result['Results'][key]) for key in new_order)

    # Add the 'Top Stories' key back to the dictionary
    new_dict['Top Stories'] = top_stories_value

    # Update the original dictionary with the new order of keys
    result['Results'] = new_dict
    
    return result