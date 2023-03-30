import requests
from bs4 import BeautifulSoup
import csv


    #resultat
    header_product = ["product_page_url", "universal_product_code", "title","price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_ur"]
    product=[]

    with open('book.csv', 'w') as f:
      writer = csv.writer(f, delimiter=',')
      writer.writerow(header_product)


    url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #URL de la page du produit
    product_page_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


    # Récupération du titre du livre
    title = soup.find("h1")
    title=title.string


    # Obtain information from tag <table>
    table1 = soup.find("table", class_="table table-striped")

    valeur_table = []
    for i in table1.find_all("td"):
        valeur = i.text
        valeur_table.append(valeur)

    universal_product_code = valeur_table[0]
    category = valeur_table[1]
    price_excluding_tax = valeur_table[2]
    print(price_excluding_tax)
    #price_excluding_tax = price_excluding_tax[1:]
    price_including_tax = valeur_table[3]
    #price_including_tax = price_including_tax[1:]
    number_available = valeur_table[5]



    #Récuperation de la description du produit par meta
    """description_raw = soup.select('meta', {'name' : 'description'})
    description = description_raw[2]
    print(description_raw[2].attrs["content"])
    #description = description.string
    print(description)"""

    # Récupération de la description du produit par <p>
    product_description = soup.find("p", class_=False )
    product_description=product_description.string

    # Récupération du rating
    if soup.find("p", class_= "star-rating One" ) != None:
        review_rating = 1
    elif soup.find("p", class_= "star-rating Two" ) != None:
        review_rating = 2
    elif soup.find("p", class_= "star-rating Three" ) != None:
        review_rating = 3
    elif soup.find("p", class_= "star-rating For" ) != None:
        review_rating = 4
    elif soup.find("p", class_= "star-rating Five" ) != None:
        review_rating = 5
    else :
        review_rating = 0


    # Récupération de l'image
    for item in soup.find_all('img'):
        image_url= 'http://books.toscrape.com/' + item['src']

    product = [product_page_url, universal_product_code, title,price_including_tax, price_excluding_tax,
               number_available, product_description, category, review_rating, image_url]

    with open('book.csv', 'a') as f:
      writer = csv.writer(f, delimiter=',')
      writer.writerow(product)



    #product_dict = {"product_page_url":"", "universal_product_code":"", "title":"","price_including_tax":"", "price_excluding_tax":"",
    #           "number_available":"", "product_description":"", "category":"", "review_rating":"", "image_url":""}

