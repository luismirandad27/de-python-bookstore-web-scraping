import requests
import json
from bs4 import BeautifulSoup

url = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=Vancouver%2C+British+Columbia"
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id='main-content')

navigation = results.find('div',class_="pagination__09f24__VRjN4")
total_pages_div = navigation.find_all('div',recursive=False)[1]
total_pages_span = total_pages_div.find('span')
total_pages = int(total_pages_span.text.split(' ')[2])

for i in range(0,total_pages):
    start = i * 10
    url = f"https://www.yelp.com/search?find_desc=Restaurants&find_loc=Vancouver%2C+British+Columbia&start={start}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id='main-content')

    results = results.find_all('h3',class_='css-1agk4wl')

    for element in results:
        # Getting the Restaurant Name
        restaurant_name = element.text

        # Moving back to the div related to the restaurant
        previous = element.find_previous('div')
        previous = previous.find_previous('div')
        previous = previous.find_previous('div')
        previous = previous.find_previous('div')

        # Getting the div element for rating and tags
        div_rating = previous.find_all('div',recursive = False)[1]
        div_tags = previous.find_all('div',recursive = False)[2]

        # Getting the total reviews
        div_rating = div_rating.find('div')
        div_rating = div_rating.find('div')
        div_rating = div_rating.find('div')
        div_rating = div_rating.find_all('div',recursive=False)

        # Getting the rating value for the restaurant
        span_rating = div_rating[0].find('span')
        div_rating_f = span_rating.find('div')
        rating_value = div_rating_f['aria-label']

        span_reviews = div_rating[1].find('span',class_='css-chan6m')
        rating_total_reviews = span_reviews.text
        
        # Getting the tags
        p_element = div_tags.find('p')
        tag_elements = p_element.find_all('span')[0]
        tag_elements = tag_elements.find_all('a')

        print(f"{restaurant_name}: {rating_value} (Total reviews: {rating_total_reviews})")
        print('TAGS:')
        for tag_element in tag_elements:
            span_element = tag_element.find('span',class_='css-11bijt4')
            print(span_element.text)




