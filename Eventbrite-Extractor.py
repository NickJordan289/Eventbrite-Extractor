# Created by Nick Jordan
# https://github.com/NickJordan289/Eventbrite-Extractor
# Simple tool to extract features from eventbrite pastevents page

import os
from bs4 import BeautifulSoup
import requests
import json
from argparse import ArgumentParser
import click  # progress bar
from urllib.parse import unquote
from urllib.request import urlretrieve

# TODO: use selenium for "show more" past event expanding

parser = ArgumentParser()
parser.add_argument('-t', '--target', required=True, dest='target',
                    help='target URL or HTML file to read from', metavar='FILE')
parser.add_argument('-i', '--images', dest='images',
                    action='store_true', help='should download images')
parser.add_argument('-n', '--no-images', dest='images',
                    action='store_false', help='no images will be downloaded')
parser.add_argument('-o', '--output', dest='output_dir',
                    help='where to put output', default='./output/')
parser.set_defaults(images=True)

args = vars(parser.parse_args())
target = args['target']
dl_images = args['images']
output_dir = args['output_dir']

# create output dir using relative path
os.makedirs(os.getcwd()+'/'+output_dir, exist_ok=True)

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

output = {'events': []}

events = soup.findAll('div', class_='list-card-v2')
with click.progressbar(events, label='Processing events') as events:
    for event in events:
        new_event = {}
        new_event['url'] = event.get('data-share-url')
        new_event['date'] = ' '.join(
            event.find('time', class_='list-card__date').string.replace('\n', '').split())
        new_event['title'] = event.find(
            'div', class_='list-card__title').string.strip()
        new_event['venue'] = event.find(
            'div', class_='list-card__venue').string.strip()

        img = event.find('img', class_='js-poster-image').get('src')
        img_url = None
        if 'files/' in img:  # using a saved html
            img = img.split('files/')[1]  # remove prefix that html save gives
        else:  # using live version
            img_url = img = unquote(img).split(
                'img.evbuc.com/')[1].split('?')[0]  # live url fixing

        # encode image name same way that chromium html save does (for consistency)
        image_name = img.replace('.', '_').replace(
            '/', '_').replace(':', '_').replace('original_', 'original.')

        # hacky fix, TODO: fix above so that we dont need to do this
        image_name = image_name.replace('cdn_evbuc_com', 'cdn.evbuc.com')

        new_event['image'] = image_name

        # save file from url as image_name at output_dir/images
        if img_url and dl_images:
            os.makedirs(os.getcwd()+'/'+output_dir+'/images/', exist_ok=True)
            urlretrieve(img_url, os.getcwd()+'/'+output_dir+'/images/'+image_name)

        output['events'].append(new_event)

with open(os.getcwd()+'/'+output_dir+'/'+'output.json', 'w') as file:
    json.dump(output, file, sort_keys=True, indent=2)
