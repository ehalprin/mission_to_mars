# Import splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate a headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title" : news_title,
        "news_paragraph" : news_paragraph,
        "featured_image" : featured_image(browser),
        "facts": mars_facts(),
        "mars_hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Quit
    browser.quit()
    return data

# Create a function:
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Set up HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.spaceimages-mars.com/{img_url_rel}'

    return img_url

# Mars Facts
def mars_facts():
    try:
        # Create DF from website
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes=["table table-bordered table-striped"])

def mars_hemispheres(browser):
    # Visit main URL
    main_url = 'https://marshemispheres.com/'
    browser.visit(main_url)

    # Scrape main URL HTML
    html = browser.html
    hm_soup = soup(html, 'html.parser')

    # List for hemisphere URLs and titles
    hemisphere_image_urls = []

    # Loop through hemispheres to collect URLs and titles
    for h in range(0,4):
    
        # Create an empty dictionary
        hemispheres = {}

        # Select the 'results' section of the main URL
        results_elem = hm_soup.select_one('div.full-content')

        # Select the 'h' result
        result_item = results_elem.find_all('div', class_='item')[h]

        # Find the specific link associated with the 'h' result
        href = result_item.find('a', class_='itemLink product-item').get('href')

        # Visit the page for the 'h' result
        browser.visit(f'{main_url}{href}')

        # Scrape the HTML from the 'h' result URL
        new_html = browser.html
        new_soup = soup(new_html, 'html.parser')

        # Get the URL for the high resolution photo
        hm_url_rel = new_soup.find('img', class_='wide-image').get('src')
        hm_url = f'{main_url}{hm_url_rel}'

        # Get the title for the hemisphere
        hm_title = new_soup.select_one('h2').get_text()

        # Create a dictionary for the hemisphere data
        hemispheres = {'img_url': hm_url, 'title': hm_title}

        # Add the hemisphere data to the list
        hemisphere_image_urls.append(hemispheres)

        # Go back to start over
        browser.back
    
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())