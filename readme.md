# My Collection of Python scripts

Here are some of my Python scripts that I've made for various Fiverr customers. I'll give a small description of the requirements for every script that is listed here, below.

# crawler-LancasterProperties (27 June 2019)
- The customer wanted to go through each property on the Lancaster County website. In the URL, the property ID is given. This ID can be changed in the URL, so a new property gets pulled up.
- The script should download the "Datasheet" PDF from the URL (near the top of the page) and convert every table from the file in a separate CSV file
- Also for every property there is a "Treasurer Info" link, with two tables regarding "payment history". The script should all the payment history data that is available.

# crawler-YouTube (14 April 2019)
- The customer needed parsing script that collects today's posted YouTube videos only. He required that  "title, description, video id, closed caption(subtitles)" details should pe inserted into a MySQL database.

# crawler-RSS (06 March 2019)
- The customer wanted a python script to put a few rss feeds in and get the title and summary out in a text file with markdown formatting for the header and body
- He also required that it tracks the title article so in case he runs the script every hour, it doesn't duplicate articles in the .txt file
