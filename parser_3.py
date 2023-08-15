import requests
from bs4 import BeautifulSoup
import os
import random
import time
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import csv

load_dotenv()

proxy_list = []
proxy_user = os.getenv('proxy_user')
proxy_password = os.getenv('proxy_password')
Image.MAX_IMAGE_PIXELS = 300000000 

with open('proxies.txt', 'r') as f:
    proxies = f.read().split('\n')
    for proxy in proxies:
        proxy_list.append({
            'http': f"http://{proxy_user}:{proxy_password}@{proxy}",
            'https': f"https://{proxy_user}:{proxy_password}@{proxy}", 
        }
    )

print(proxy_list)
    
cookies = {
    '_ga': 'GA1.2.355474566.1688918118',
    '_fbp': 'fb.1.1688918119209.1138937444',
    'JAVASCRIPT': '1',
    '_gid': 'GA1.2.809913594.1690738001',
    'PHPSESSID': 'ni5cvchllc6rohcq3m69n9llg3',
    '_ga_W07YKRLB5N': 'GS1.2.1691327548.21.1.1691327725.60.0.0',
}

headers = {
    'authority': 'www.logolounge.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': '_ga=GA1.2.355474566.1688918118; _fbp=fb.1.1688918119209.1138937444; JAVASCRIPT=1; _gid=GA1.2.809913594.1690738001; PHPSESSID=ni5cvchllc6rohcq3m69n9llg3; _ga_W07YKRLB5N=GS1.2.1691327548.21.1.1691327725.60.0.0',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

def get_links():
    logo_hrefs = []
    with open("logolounge_links.txt", "w") as f:
        for i in range(1,4131):
            print(f'crawling page {i} ...')
            url_to_scrape = 'https://www.logolounge.com/logos?page='+str(i)
            response = requests.get(url_to_scrape, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            logo_items = soup.find_all('article', class_='logo-item')
            for logo in logo_items:
                href = logo.find('a', class_='logo-item-figure-content')['href']
                f.write('https://www.logolounge.com/' + href + '\n')

    print('done')
    
def save_img(url, fileName, proxy):
    response = requests.get(url, stream=True, cookies=cookies, headers=headers, proxies=proxy)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))

    if img.mode == "CMYK":
        img = img.convert("RGB")

    img.info.pop('icc_profile', None)
    
    if not os.path.exists('./logos3'):
        os.makedirs('logos3')

    img.thumbnail((512, 512))
    
    fileName = fileName.replace('/','')
    try:
        img.save(f'./logos3/{fileName}', "PNG")
    except:
        csv_file = 'long_name.csv'
        fileName_new = fileName[:254]
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['file_name', 'text'])
                writer.writerow([fileName_new, fileName])
                img.save(f'./logos3/{fileName_new}', "PNG")
        else:
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([fileName_new, fileName])
                img.save(f'./logos3/{fileName_new}', "PNG")

def process_link(link, proxy):
    link = link.replace("\n", "")
    dd_client = ''  # Initialize dd_client as an empty string

    try:
        start_time = time.time()
        response = requests.get(link, cookies=cookies, headers=headers, proxies=proxy)
        end_time = time.time()
        response_time = end_time - start_time
        response_time= round(response_time, 2)
        # print('check point 0')
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        
        #get name and tags
        try:
            # print('check point a')
            dd_client = soup.find('h1', class_='vcard-heading').text.replace('\n','')    
            fileName = dd_client
            
            # print('check point b')
            dt_industry = soup.find('dt', string='Industry')        
            dd_industry = dt_industry.find_next('dd').text
            fileName = '_'.join([dd_client, dd_industry]).replace('/', ' ')
                    
            # print('check point c')
            dd_tags = dt_industry.find_next('dd').find_next('dd').text.replace('\n','')
            dd_tags = ' '.join(set(dd_tags.split()))
            
            # print('check point d')
            fileName = '_'.join([dd_client, dd_industry, dd_tags]).replace('/', ' ').replace(' .png', '.png')
            fileName = fileName + '.png'
            words_to_replace = ['design', 'logo', 'image', 'icon', 'Icon']
            for word in words_to_replace:
                fileName = fileName.replace(word, '')
        except:
            fileName = dd_client + '.png'
                    
        if len(fileName) < 255:         #skip short names to download long names only
            print('skip...')
            return
            
        #get logo img and save it
        figure = soup.find('figure', class_='single-logo-figure')
        img_url = figure.find('img')['src']
       
                
        #save img
        print('--------------------- ✅')
        print(f'saving img of {link}...')
        print(f'client = {dd_client}')
        print(f'file name = {fileName}')
        print(f'name length = {len(fileName)}')
        print(f'{img_url}')
        print('Response time: {} seconds'.format(response_time))
        print('---------------------\n')
        save_img(img_url, fileName, proxy)
            
    except Exception as e:
        print('--------------------- ❌')
        print(f'something went wrong with {link}')
        print(f"An error occurred: {e}")
        print('---------------------\n')
        with open("logolounge_scrap_failure.txt", "a") as f:
            f.write(link + '\n')


def scrap():
    file = "logolounge_links.txt"
    start_count = 248337
    count = 0
    
    with open(file, 'r') as f:
        links = f.readlines()
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        for link in links:
            
            # if count > 0:
            #     break
            print(f'iteration {count}')
            if count >= start_count:
                executor.submit(process_link, link, random.choice(proxy_list))
                time.sleep(random.random()+0.2)
            count += 1

scrap()