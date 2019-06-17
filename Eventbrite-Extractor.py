from bs4 import BeautifulSoup # pip install beautifulsoup4
import requests
import json
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-t', '--target', required=True, dest='target',
                    help='target URL or HTML file to read from', metavar='FILE')
parser.add_argument('-i', '--images', dest='images', action='store_true', help='should download images')
parser.add_argument('-n', '--no-images', dest='images', action='store_false', help='no images will be downloaded')
parser.set_defaults(images=True)

args = vars(parser.parse_args())
target = args['target']
dl_images = args['images']

try:
    if ('.html' in target):
        with open(target, encoding='utf-8') as file:
            html = file.read()
    else:
        html = requests.get(target).content
except Exception as e:
    print('Please provide a valid html file or a url beginning in http://')
    exit()

soup = BeautifulSoup(html, 'html.parser')

events = soup.findAll('div', class_='list-card-v2')
print(events[0].get('data-share-url'))