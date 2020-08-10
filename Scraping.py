# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

# create a function to initiate the browser
def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # set our news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p

# ### JPL Space Images Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')


    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

# ### Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[1]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# ***CHALLENGE***
def hemispheres(browser):

    # Visit the Mars Hemisphere url
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Parse the resulting html with BeautifulSoup
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    hemi_soup_url = hemi_soup.find_all('div', class_= "item")

    # Create an empty list to store the dictionnary with 'img_url' and 'title'
    hemisphere_image_urls = []

    #loop through the 4 urls 
    for item in hemi_soup_url:
        hemisphere_url = item.find('a', class_ = "itemLink product-item")['href']
        hemisphere_click = 'https://astrogeology.usgs.gov' + hemisphere_url
        browser.visit(hemisphere_click)
        
        # Parse the resulting hemi_html with BeautifulSoup
        hemi_html = browser.html
        hemi_soup = BeautifulSoup(hemi_html, 'html.parser')

        title = hemi_soup.find('h2', class_= "title").text.rstrip("Enhanced")
        img_url = hemi_soup.find('div', class_ = "downloads").find('li').find('a')['href']

        #Create an empty dictionary to store 'img_url' and 'title'
        hemisphere_dict = {}

        #Create a key for the dictionary for title "hemisphere_dict"
        hemisphere_dict['title'] = title

        #Create a key for the dictionary for img_url "hemisphere_dict"
        hemisphere_dict['img_url'] = img_url

        #append dictionary to list
        hemisphere_image_urls.append(hemisphere_dict)

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())