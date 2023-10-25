from bs4 import BeautifulSoup
import os
from joblib import Parallel, delayed
import multiprocessing
from tqdm import tqdm
import json
import requests

main_page_url = 'https://almeera.online/'
output_jsons_path = '../Data/Category JSONs'
output_images_path = '../images'


class AlmeeraScrapper:
    def __init__(self, main_page_url, output_jsons_path, output_images_path):
        self.main_page_url = main_page_url
        self.output_jsons_path = output_jsons_path
        self.output_images_path = output_images_path

    def url_to_soup_obj(self, url):
        """Fetch and parse a web page into a BeautifulSoup object."""
        headers = {
            'authority': 'almeera.online',
            'method': 'GET',
            'scheme': 'https',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ur;q=0.7',
            'Cache-Control': 'max-age=0',
            'Dnt': '1',
            'Referer': 'https://almeera.online/',
            'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "Windows",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }

        while True:
            try:
                response = requests.get(url, headers=headers)
                break
            except Exception as e:
                print(e)

        soup_obj = BeautifulSoup(response.content, 'html.parser')
        return soup_obj

    def download_image(self, image_url, image_path):
        """This function will get an image url and output local image path. And download the image"""

        if not os.path.exists(image_path):
            # Fetch the image
            response = requests.get(image_url)

            # Get the size of the response content in bytes
            response_size = len(response.content)

            if response_size < 1000:
                raise ('Empty Image ...!')

            # Check if the request was successful
            if response.status_code == 200:
                # Open a new file in binary mode ('wb')
                with open(image_path, "wb") as f:
                    # Write the image data to the file
                    f.write(response.content)

    def sub_categorise_extractor(self, sub_category_url, category_name):
        """Extract information about a subcategory and its products.

        Parameters:
        sub_category_url: The URL representing the subcategory page.

        Returns:
        dict: A dictionary containing subcategory information and a list of products.
        """

        sub_category_dict = {}

        sub_category_page_soup = self.url_to_soup_obj(sub_category_url)

        sub_category_title = sub_category_page_soup.find('h1', attrs={'id': 'page-title'}).text.strip()

        # generate sub-category folder
        sub_folder_path = os.path.join(self.output_images_path, category_name, sub_category_title)
        if not os.path.exists(sub_folder_path):
            os.makedirs(sub_folder_path)

        sub_category_dict['SubcategoryTitle'] = sub_category_title

        products_list = []
        try:
            products_element = sub_category_page_soup.find('div', attrs={'class': 'products'}).find_all('li', attrs={
                'class': 'product-cell box-product'})
        except:
            return sub_category_dict


        # Extracting products data
        for product_element in products_element[:5]:
            product_dict = {}

            # getting product title
            item_title = product_element.find('h5', attrs={'class': 'product-name'}).text.strip()
            product_dict['ItemTitle'] = item_title

            # getting product image url
            item_image = product_element.find('div', attrs={'class': 'product-photo'}).find('img').get('src')
            image_url = 'https:' + item_image
            product_dict['ItemImageURL'] = image_url

            output_image_path = os.path.join(self.output_images_path, category_name, sub_category_title,
                                             os.path.basename(image_url))
            self.download_image(image_url, output_image_path)

            # getting product price
            item_price = product_element.find('ul', attrs={'class': 'product-price'}).find('span', attrs={
                'class': 'price'}).text.strip()
            product_dict['ItemPrice'] = item_price

            product_page_url = 'https://almeera.online/' + product_element.find('h5',
                                                                                attrs={'class': 'product-name'}).find(
                'a').get('href')

            product_page_soup = self.url_to_soup_obj(product_page_url)
            item_sku = product_page_soup.find('li', attrs={'class': 'product-sku'}).find('span', attrs={
                'class': 'value'}).text.strip()
            product_dict['ItemBarcode'] = item_sku

            products_list.append(product_dict)

        sub_category_dict['Products'] = products_list

        return sub_category_dict

    def process_category(self, category_element):
        category_dict = {}

        # getting category title
        category_name = category_element.find('a').text.strip()
        category_dict['CategoryTitle'] = category_name
        # print(f'Extracting : {category_name} ...!')

        # generate category folder
        folder_path = os.path.join(self.output_images_path, category_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Getting category image
        category_url = self.main_page_url + category_element.find('a').get('href')
        category_soup = self.url_to_soup_obj(category_url)

        try:
            category_image_url = 'https:' + category_soup.find('div', attrs={'class': 'category-banner'}).find(
                'img').get('src')

            # downloading image if available
            self.download_image(category_image_url,
                                os.path.join(self.output_images_path, category_name, 'category_image.jpg'))
        except:
            category_image_url = None
        category_dict['CategoryImageURL'] = category_image_url

        category_dict['Subcategories'] = []
        # getting sub categories
        sub_categories_list = category_element.find('ul', attrs={'class': 'menu'}).findChildren(recursive=False)
        for sub_category in sub_categories_list:
            sub_category_name = sub_category.find('a').text.strip()
            sub_category_url = self.main_page_url + sub_category.find('a').get('href')

            sub_category_dict = self.sub_categorise_extractor(sub_category_url, category_name)

            sub_category_dict['SubcategoryTitle'] = sub_category_name

            category_dict['Subcategories'].append(sub_category_dict)

        with open(os.path.join(self.output_jsons_path, category_name + '.json'), 'w') as obj:
            json.dump(category_dict, obj, indent=4)

    def main(self):
        """Main function to extract category, subcategories, and products data.

        Fetches and processes the main page content, extracts category and subcategory details,
        then applies multi-processing to extract data in parallel. Finally, saves the result
        in a JSON file.
        """
        soup = self.url_to_soup_obj(main_page_url)

        # Extracting categories
        categories_main_div = soup.find('ul', attrs={'class': 'catalog-categories-tree'})
        categories_div_list = categories_main_div.findChildren(recursive=False)

        num_cores = multiprocessing.cpu_count() * 2
        Parallel(n_jobs=num_cores, prefer="threads")(
            delayed(self.process_category)(category_element) for category_element in tqdm(categories_div_list))


class_obj = AlmeeraScrapper(main_page_url, output_jsons_path, output_images_path)
class_obj.main()
