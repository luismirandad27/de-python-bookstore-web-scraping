'''
This Python file is made for scraping a "Book Store Website": a fictional web page which its main purpose is to practice web scrapping.

In this case, I'm using the BeautifulSoup library to extract the HTML elements and extract the data. Finally, I'm exporting the data into a CSV file and reading it with pandas.

Author: Luis Miguel Miranda
Date: 2022-12-28
'''

# Importing libraries
import requests
import re
from bs4 import BeautifulSoup
import csv
import pandas as pd


def getting_book_catalogue():
    """
    Get the book catalogue
    
    Parameters:
    * No parameter required *
    
    Returns:
    list(String): The book catalogue
    """

    book_category_list = []

    url = "https://books.toscrape.com"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find('div',class_="container-fluid page")
    div_sidebar = results.find('aside',class_="sidebar")
    list_books_li = div_sidebar.find_all('li')

    for li_element in list_books_li:
        book_category_a = li_element.find('a')
        book_category_list.append(book_category_a.text.strip().lower())
    
    return book_category_list

def scraping_bookstore_webpage(book_category_list):
    """
    Scraping the website to obtain the basic info per each book.
    1) Accessing the page with the list per each book category (url: ...../category/books/{book_category}/index.html)
    2) If the book category has more than 20 books, it would have more than 1 html 
    3) Inside the HTML for the list of 1 book category, we have a link to each book. I'm getting the HTML of each book too.
    
    Parameters:
    * No parameter required *
    
    Returns:
    list(String): The book catalogue
    """

    with open('bookstore_scraping.csv', mode='w') as bookstore_file:

        bookstore_writer = csv.writer(bookstore_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        book_header = ['Book Row','Book Name','Book URL','Book Category','Book Price','Book UPC','Book Availability','Books Available','Book Reviews','Book Rating']

        bookstore_writer.writerow(book_header)

        book_id = 1

        for idx in range(1,len(book_category_list)):
            
            book_category_for_url = str.replace(book_category_list[idx],' ','-')
            
            url = f"https://books.toscrape.com/catalogue/category/books/{book_category_for_url}_{idx+1}/index.html"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # Getting the number of pagess
            results = soup.find('div',class_="container-fluid page")
            page_inner = results.find('div',class_="page_inner")
            row = page_inner.find('div',recursive=False)
            books_div = row.find('div',recursive=False)
            books_list_section = books_div.find('section',recursive=False)
            
            books_pager_ul = books_list_section.find('ul',class_="pager")
            if (books_pager_ul is None):
                books_total_pages = 1
            else:
                books_pager_current = books_pager_ul.find('li',class_="current").text.strip()
                books_total_pages = int(books_pager_current.split(' ')[3])

            for idx_page in range(0,books_total_pages):
                
                #If the book category contains more than 1 page, I'm changing the URL
                if (books_total_pages != 1):
                    url = f"https://books.toscrape.com/catalogue/category/books/{book_category_for_url}_{idx+1}/page-{idx_page+1}.html"

                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")

                # Getting the number of pagess
                results = soup.find('div',class_="container-fluid page")
                page_inner = results.find('div',class_="page_inner")
                row = page_inner.find('div',recursive=False)
                books_div = row.find('div',recursive=False)
                books_list_section = books_div.find('section',recursive=False)

                books_list_li = books_list_section.find('ol',class_="row")
                books_list_li = books_list_li.find_all('li')

                for list_li_element in books_list_li:

                    list_li_article = list_li_element.find('article',recursive=False)

                    # Book's name
                    name_h3 = list_li_article.find('h3',recursive=False)
                    name_a = name_h3.find('a')
                    book_link = str.replace(name_a['href'],'../../../','https://books.toscrape.com/catalogue/')
                    book_name = name_a['title']

                    page_book = requests.get(book_link)
                    page_soup = BeautifulSoup(page_book.content,"html.parser")
                    page_div = page_soup.find('div',class_="container-fluid page")
                    page_inner = page_div.find('div',class_="page_inner")
                    page_content_table = page_inner.find('table')
                    page_content_rows = page_content_table.find_all('tr')
                    book_upc = page_content_rows[0].find('td').text
                    book_stock = page_content_rows[5].find('td').text

                    book_stock_availability = re.findall('^[^\(]+',book_stock)[0].strip()
                    book_stock_value = re.findall("\(.+?\)",book_stock)[0]
                    book_stock_value = str.replace(book_stock_value,'(','')
                    book_stock_value = str.replace(book_stock_value,')','').split(' ')[0]

                    book_review = page_content_rows[6].find('td').text
                    
                    # Book's Rating
                    rating_p = list_li_article.find('p',recursive=False)
                    rating_value = rating_p['class'][1]
                    
                    match rating_value:
                        case "One":
                            rating_value = 1 
                        case "Two":
                            rating_value = 2
                        case "Three":
                            rating_value = 3
                        case "Four":
                            rating_value = 4
                        case "Five":
                            rating_value = 5
                        case default:
                            rating_value = 0
                    
                    # Book's Price
                    price_div = list_li_article.find('div',class_="product_price")
                    book_price = str.replace(price_div.find('p',class_="price_color").text,'£','')
                    
                    book_element = [book_id, book_name, book_link,book_category_list[idx],book_price,book_upc,book_stock_availability,book_stock_value,book_review,rating_value]
                    
                    book_id += 1

                    bookstore_writer.writerow(book_element)

        print('The Scraping Process on the Book Store website has been finished!')

def getting_total_books_per_category():
    """
    Reading the csv file to a pandas' dataframe and making some aggregations
    
    Parameters:
    * No parameter required *
    
    Returns:
    * No return value required *
    """

    df = pd.read_csv('bookstore_scraping.csv')
    
    df_count = df[['Book Row','Book Category','Book Price']]\
                    .groupby(['Book Category'])\
                    .agg({'Book Row':'count','Book Price':['sum','mean','min','max']})\
                    .sort_values(by=[('Book Row','count')],ascending=False)
    
    #Keeping the top 10 (based on the Book count)
    df_count = df_count.head(10)

    #Printing ranking of book categories
    print(df_count)

def _init_():
    """
    Main function
    
    Parameters:
    * No parameter required *
    
    Returns:
    * No return value required *
    """
    book_category_list = getting_book_catalogue()
    scraping_bookstore_webpage(book_category_list)
    getting_total_books_per_category()

_init_()
