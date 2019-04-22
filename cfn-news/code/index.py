import os
import re
from datetime import datetime, timedelta, date
from urllib.request import Request, urlopen

from botocore.vendored import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/ReleaseHistory.html?shortFooter=true'


def handler(event, context):
    now = datetime.utcnow()
    since = (now - timedelta(days=7)).date()
    results = get_news(download_html(), since)
    if len(results) == 0:
        print('No news')
        return
    html = 'Cloudformation service updates since {0}:\n'.format(since.strftime('%d %B %Y'))
    for result in results:
        description = result['description']
        description = re.sub(r'\n+', '\n', description).strip()
        html += """<b>{0} {1}</b>\n{2}\n\n""".format(result['date'].strftime('%d %B %Y'),
                                                   result['change'], description)
    html += '\nSource: {0}'.format(url)
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                             json={'chat_id': chat_id, 'text': html, 'parse_mode': 'html'})
    result = response.json()
    return result


def get_news(html_doc, get_releases_since_date: date = None):
    if get_releases_since_date:
        print('Getting news since', get_releases_since_date)
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.select('div.table-contents table')[0]
    results = []
    for row_index, row in enumerate(table.find_all('tr')):
        if row_index == 0:
            continue
        row_result = {}
        for column_index, td in enumerate(row.find_all('td')):
            column_names = {
                0: 'change',
                1: 'description',
                2: 'date'
            }
            text = td.text.strip()
            if column_index == 2:
                date_value = parse(text).date()
                row_result[column_names[column_index]] = date_value
            else:
                re.search('\w+::\w+::\w+', text)
                text = re.sub('\w+::\w+::\w+', '<i>\g<0></i>', text)
                text = re.sub('\.', '.\n', text)
                row_result[column_names[column_index]] = text
        if get_releases_since_date is None or get_releases_since_date < row_result['date']:
            print(row_result['date'].strftime('%d %B %Y'), row_result['change'])
            results.append(row_result)
        if row_index == 10:
            break

    return results


def download_html():
    request = Request(url)
    return urlopen(request).read()


if __name__ == '__main__':
    # open('data.html', 'w').write(html_doc.decode('utf-8'))
    html_doc = open('data.html').read()
    get_news(html_doc, parse('2018-05-01 12:34:45.789').date())
