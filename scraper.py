#! python3

import requests
from bs4 import BeautifulSoup
    
def build_pages():
    '''
    Build all the main page URLs (i.e. a.php, b.php etc.)
    '''
    sequence = 'abcdefghijklmnopqrstuvwxyz0123456789'
    urls = ['https://www.thelayoff.com/' + char + '.php' for char in sequence]
    return urls


def build_subpages():
    '''
    Build all the subpage URLs for each letter and group them in a list.
    '''
    detailedUrls = []
    urls = build_pages()
    for url in urls:
        i = 1
        while True:
            buildUrl = url + '?page=' + str(i)
            finalUrl = BeautifulSoup(requests.get(buildUrl).text, 'html.parser')
            if finalUrl.find('ul', 'abc-list').get_text().strip() is not '':
                companyDetails = finalUrl.select('#content > div > ul.abc-list > li > a')
                for x in range(len(companyDetails)):
                    detailedUrls.append('https://www.thelayoff.com' + companyDetails[x]['href'])
                i += 1
            else:
                break
    return detailedUrls


def get_company_details(url):
    '''
    Parse a url and get all the company details (if available):
    Post Title, Content, IDs, Dates, Views and Replies.
    '''
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')
    companyName = html.h1.get_text()[:-8]

    temp = []
    if len(html.find_all('article')) > 0:
        for article in html.find_all('article'):
            postTitle = article.find('h2', 'post-title').get_text().strip().replace(';', '')
            try:
                postContent = article.find('div', 'post-body').get_text().strip().replace('\n', ' ').replace(';', '')
                if postContent[-9:] == 'read\xa0more':
                    postContent = postContent[:-13]
            except AttributeError:
                postContent = ''
            try:
                postId = article.find('span', 'postid').get_text().strip()
            except AttributeError:
                postId = ''
            postDate = article.time.get('datetime')[:10]
            postViews = article.find('span', 'views').get_text()
            temp.append('|'.join((companyName, postTitle, postContent, postId, postDate, postViews)))
        return temp
    else:
        return(['|'.join((companyName, 'No posts available'))])
    
file = 'layoff.csv'

with open(file, 'w', encoding='utf-8') as f:
    f.write('Company Name|Title|Content|Post ID|Post Date|Number of Views\n')
    subpages = build_subpages()
    for link in subpages:
        x = get_company_details(link)
        if len(x) == 1:
            f.write(x[0] + '\n')
        else:
            for elem in x:
                f.write(elem + '\n')
print('Data parsed successfully')