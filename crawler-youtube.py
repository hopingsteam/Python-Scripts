# Fiver order no. FO17FFC460B4
# Buyer: #
# Author: Mihai-Alexandru Matraguna

import youtube_dl
import requests
import json
import os
import sys
from os import environ, getcwd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import shutil
from time import sleep
from random import randint

'''
We are using youtube API v3 to query youtube. 
set limit and query here. ALternatively it can pick queries from a text file. 
You need to create your own API key using google developers tools.
API returns a json response which is parsed to python object using response.json() method.
'''
limit = 50
API_KEY = 'AIzaSyBV-RjjXUxhYTIsT6LbRPWUCq_xtSujVrQ'
date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
date_today = datetime.today().strftime('%Y-%m-%d') + "T00:00:00.000Z"
queries_list = ["man weave unit", "hairclub", "bosley", "alopecia"]
queries_line = ""
if len(sys.argv) > 1:
    queries = sys.argv[1:]
    for query in queries:
        queries_line += str(query)
    queries_list = queries_line.split(",")

else:
    print("please add keywords separated by \",\"")


def save(uid, thumbnail_url, dirname):
    sleep(0.5)
    print('  [+] Getting image {}'.format(uid))
    image = requests.get(thumbnail_url, stream=True)
    if image.status_code == 200:
        # image_path = '{}.jpg'.format(uid)
        image_path = 'C:/inetpub/vhosts/modernnewhair.com/httpdocs/images/thumbs/{}.jpg'.format(uid)
        #image_path = 'thumbs/{}.jpg'.format(uid)

        with open(image_path, 'wb') as f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
        return image_path
    else:
        return 'Null'


for q in queries_list:
    print('  [!][ANALYZING QUERY]: ' + q)
    params = {

        "q": q,
        "key": API_KEY,
        "part": "id,snippet",
        "maxResults": limit,
        "publishedAfter": date_today
    }
    response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)

    data = response.json()['items']
    print('  [!][' + str(len(data)) + ' items]')
    '''
    We have the data now, time to parse it and save it to the database. First refine the result.
    '''
    refined_data = []
    for i in data:
        if (i['id'].get('videoId')):
            ydl_opts = {"skip_download": True,
                        "writesubttiles": True,
                        "writeautomaticsub": True,
                        "quiet": True,
                        "outtmpl": 'closedcaption/%(id)s',
                        "outtmp": 'closedcaption/%(id)s'}

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([i['id'].get('videoId')])

            subtitles_string = "No Subtitles"
            try:
                with open('closedcaption/' + i['id'].get('videoId') + '.en.vtt', 'r') as content_file:
                    subtitles_string = content_file.read()
            except:
                print('  [!] No subtitle found')

            refined_data.append({
                'title': i['snippet']['title'],
                'description': i['snippet']['description'],
                'closed_caption': subtitles_string,
                'publishedAt': i['snippet']['publishedAt'],
                'thumbnail': save(i['id'].get('videoId'), i['snippet']['thumbnails']['medium']['url'], q),
                'link': i['id'].get('videoId')
            })

    '''
    We now have the refined data as required by the database Schema, i.e title, description, thumbnail, video_link
    time to push it to database. I am testing it with sqllite which with python. 
    '''

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='admin_modernnew',
                                             user='user_modernnew',
                                             password='StJohn2121^')

        """connection = mysql.connector.connect(host='localhost',
                                         database='euston102',
                                         user='root',
                                         password='')"""

        # if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL database... MySQL Server version on ", db_Info)
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS `infotube` (
                                `id` int(11) NOT NULL AUTO_INCREMENT,
                                `title_name` varchar(255) NOT NULL,
                                `description` varchar(255) NOT NULL,
                                `closed_caption` TEXT NOT NULL,
                                `closed_caption2` varchar(512) NOT NULL,                              
                                `thumbnail` varchar(255) NOT NULL,
                                `created_on` date DEFAULT NULL,
                                `updated_on` date DEFAULT NULL,
                                PRIMARY KEY (`id`),
                                UNIQUE KEY `user_name_unique` (`id`)
                                ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1''')

        for i in refined_data:
            title = i['title']
            # print ("title: "+str(title))
            dateof = i['publishedAt']
            # print ("publishedAt: "+str(dateof))
            description = i['description']
            # print ("description: "+str(description))
            thumbnail = i['thumbnail']
            # print ("thumbnail: "+thumbnail)
            video_link = i['link']
            # print ("video_link: "+video_link)
            subtitles = i['closed_caption']
            try:

                cursor.execute('''INSERT INTO infotube (title_name, description, closed_caption, closed_caption2, thumbnail, created_on, updated_on)
                                VALUES(%s, %s, %s, %s, %s, %s, %s)''',
                               (title, description, subtitles, video_link, thumbnail, date_now, date_now))
            except Exception as e:
                val = 0
                # print(e)
        connection.commit()
        print('Changes commited in the database')

    except Error as e:
        print(e)
