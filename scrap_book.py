import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import shutil

#Fonction principale qui permert de choisir la catégorie dont on souhaite les informations
def get_category_product():

    url = 'https://books.toscrape.com/index.html'
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')

        #Récupération des catégories
        links = soup.find_all("a")
        category_dict = {"All" : 'https://books.toscrape.com/catalogue/category/books_1/index.html'}
        for i in range(3, 53):
            category_link = links[i].get('href')
            category = category_link[25:]
            category_link = 'https://books.toscrape.com/' + category_link
            l = len(category)
            for j in range(l):
                if category[j] == '_':
                    category = category[:j].capitalize()
                    break
            category_dict[category] = category_link

        for key in category_dict:
            print(key)

        print('Quelle catégorie voulez-vous télécharger ?')
        category_choice = input()
        product_data_all=[]
        if category_choice in category_dict :
            if category_choice == 'All':
                # Créer le dossier 'category' dans le dossier 'book'
                book_path = Path('./book')
                book_path.mkdir(exist_ok=True)
                category_path = book_path / category_choice
                category_path.mkdir(exist_ok=True)
                for cat in category_dict :
                    if cat == 'All':
                        print('')
                    else:
                        if cat == 'Mystery':
                            break
                        print(cat)
                        url = category_dict[cat]
                        product_data = get_all_product_index(url)
                        creation_csv(cat, product_data)
                        for i in product_data:
                            product_data_all.append(i)
                creation_csv(category_choice, product_data_all)
                print(len(product_data_all))
                # déplacer le fichier book_All.csv à la racine
                src_path = './book/All/Book_All.csv'
                dst_path = './book/Book_All.csv'
                shutil.move(src_path, dst_path)
                # Effacer le dossier 'All'
                folder_path = './book/All/'
                shutil.rmtree(folder_path)

            else:
                print(category_choice)
                url = category_dict[category_choice]
                product_data = get_all_product_index(url)
                creation_csv(category_choice, product_data)
        else:
            print("Choissisez une catégorie existante")

def creation_csv(category_file, product_data):
        #création du fichier csv
        file_name_csv = 'Book_' + category_file + '.csv'
        file_path = Path.cwd() / 'book' / category_file / file_name_csv
        field_names = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax',
         'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(product_data)

#Fonction qui permet de récuperer les données de livres de l'ensemble des pages d'une catégorie
def get_all_product_index(index_url):

    response = requests.get(index_url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')

        #Nombre de pages de la catégorie
        product_number = soup.find_all("strong")
        product_number = product_number[1]
        product_number = product_number.text
        page_number = int(product_number)//20 + 1

        #Récupération racine page web
        l = len(index_url)
        rev = ''.join(reversed(index_url))
        for i in range(12):
            if rev[i] == '/':
                racine = i
                break
        root_url = index_url[:l-racine]

        #Récupération des données des produits dans toutes les pages de la catégorie
        product_list = []
        for i in range(page_number):
            print('page')
            print(i)

            if i == 0:
                url_page = root_url + 'index.html'
                product_list_page = get_product_list(url_page)
            else:
                url_page = root_url + 'page-' + str(i+1) + '.html'
                product_list_page = get_product_list(url_page)
            for product in product_list_page:
                product_list.append(product)
        return product_list

#Fonction qui permet de récuperer la listes des urls des pages des livre d'un index
def get_product_list(page_list_url):

    response = requests.get(page_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #Récupération des urls des livres de la page
    list_url=[]
    for i in soup.find_all("h3"):
        url_raw = i.find('a')
        url_raw = url_raw.get('href')
        for i in range(20):
            if url_raw[i] != '.' and url_raw[i] != '/':
                p = i
                break
        urls = 'https://books.toscrape.com/catalogue/' + url_raw[p:]
        list_url.append(urls)

    product_list = []
    for url in list_url:
        product_dict = get_product_data(url)
        product_list.append(product_dict)
    return product_list

#Fonction qui permet de récuperer les données d'une page de livre
def get_product_data(product_page_url):

    response = requests.get(product_page_url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Récupération du titre du livre
        title = soup.find("h1")
        title = title.string
        #print(title)

        # Récupération de la category du livre
        data = soup.find_all("ul", class_="breadcrumb")
        for item in data:
            category = item.find_all('a')
            category = category[2]
            category_url = category.get('href')
            category = category.text
            l_cat = len(category) + 18
            category_url = category_url[18 : l_cat : 1]

        # Récupération des données du livre dans la table d'information
        table1 = soup.find("table", class_="table table-striped")

        valeur_table = []
        for i in table1.find_all("td"):
            valeur = i.text
            valeur_table.append(valeur)

        universal_product_code = valeur_table[0]
        price_excluding_tax = valeur_table[2]
        price_including_tax = valeur_table[3]
        number_available = valeur_table[5]

        # Récupération de la description du produit par <p>

        if soup.find("div", {"id": "product_description"}):
            product_description = soup.find("p", class_= False )
            product_description = product_description.string
        else:
            product_description = ""

        # Récupération du rating
        rating = soup.find_all("div", class_="col-sm-6 product_main")
        for item in rating:
            if item.find('p', class_='star-rating One'):
                review_rating = 1
                break
            if item.find('p', class_='star-rating Two'):
                review_rating = 2
                break
            if item.find('p', class_='star-rating Three'):
                review_rating = 3
                break
            if item.find('p', class_='star-rating Four'):
                review_rating = 4
                break
            if item.find('p', class_='star-rating Five'):
                review_rating = 5
                break

        # Récupération de l'image
        for item in soup.find_all('div', class_="item active"):
            url = item.find('img')
            url = url['src']
            image_url= 'http://books.toscrape.com/' + url[6:]


        # Creation d'un dossier pour la categorie

        # Créer le dossier 'book' dans le dossier courant
        book_path = Path('./book')

        # Créer le dossier de la categorie dans le dossier 'book'
        category_path = book_path / category_url
        category_path.mkdir(exist_ok=True)
        l_prod_url = len(product_page_url) - 11
        file = product_page_url[37 : l_prod_url]  + '.jpg'
        file_path = Path.cwd() / category_path / file

        img_data = requests.get(image_url).content
        with open(file_path, 'wb') as handler:
            handler.write(img_data)



        product_dict = {"product_page_url":product_page_url, "universal_product_code":universal_product_code,
                    "title":title,"price_including_tax":price_including_tax, "price_excluding_tax":price_excluding_tax,
                   "number_available":number_available, "product_description":product_description, "category":category,
                    "review_rating":review_rating, "image_url":image_url}
        return product_dict


#product_page_url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
#get_product_data(product_page_url)

#get_product_list(page_list_url)

#get_all_product_index(index_url)

get_category_product()