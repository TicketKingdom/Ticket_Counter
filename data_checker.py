import requests
from bs4 import BeautifulSoup
from dateutil import parser
import time
import json


def get_event_name_and_date(url):
    if 'eventbrite.' in url:
        return check_eventbrite(url)
    elif 'bigtickets.' in url:
        return check_bigticket(url)
    elif 'etix.' in url:
        return check_etix(url)
    elif 'frontgatetickets.' in url:
        return check_frontgate(url)
    elif 'ticketweb.' in url:
        return check_ticketweb(url)
    elif 'seetickets.us' in url:
        return check_seetickets(url)
    elif 'showclix.' in url or '.thecomplexslc.' in url:
        return check_showclix(url)
    elif 'prekindle.' in url:
        return check_prekindle(url)
    elif 'tixr.' in url:
        return check_tixr(url)
    elif '24tix.' in url:
        return check_tix24(url)
    elif 'admitone' in url:
        return check_admitone(url)


def make_request(url):
    headers = {
        # 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36.',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0.',
        'referer': 'https://www.google.com/'
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200 or r.status_code == 506:
        return BeautifulSoup(r.content, 'html.parser')
    print(r.status_code, url)


def check_eventbrite(url):
    soup = make_request(url)
    try:
        name = soup.find('h1', {'class': 'text-body-large'}).text.strip()
    except:
        try:
            name = soup.find(
                'h1', {'class': 'listing-hero-title'}).text.strip()
        except:
            name = soup.find('h1', {'class': 'event-title'}).text.strip()

    try:
        date = soup.find(
            'div', {'class': 'event-details__data'}).find('meta')['content']
    except:
        try:
            date = soup.find('time', {'class': 'clrfix'}).find(
                'p').text.strip()
        except:
            date = soup.find('p', {'class': 'date-and-time'}
                             ).find('meta')['content']
    if len(date) < 2:
        date = str(soup.select(
            "#event-page > main > div.js-hidden-when-expired.event-listing.event-listing--has-image > div.g-grid.g-grid--page-margin-manual > div > section.listing-info.clrfix > div.listing-info__body.l-sm-pad-vert-0.l-sm-pad-vert-6.clrfix.g-group.g-group--page-margin-reset > div > div > div.g-cell.g-cell-12-12.g-cell-md-4-12.g-offset-md-1-12.g-cell--no-gutters.l-lg-pad-left-6 > div > div:nth-child(4) > meta:nth-child(1)")).split('\"')[1]
    date = date.replace('–', ' ').strip()
    if date.find('-') > 0:
        date = date.replace('-', ' ').strip()
    date = parser.parse(date).strftime('%Y-%m-%d')
    try:
        loc = [x.find_next('div', {'class': 'event-details__data'}) for x in soup.find_all(
            'h3', {'class': 'label-primary l-mar-bot-2'}) if 'Location' in x.text][0]
        loc = loc.find_all('p')
        venue, loc = loc[0].text.strip(), loc[2].text.strip()
        name = name + " {} {}".format(venue, loc)
    except:
        loc = soup.find('section', {'aria-labelledby': 'location-heading'}).find(
            'div', {'class': 'detail__content'}).find('p').text.strip()
        name = name + " {}".format(loc)
    return name, date


def check_bigticket(url):
    soup = make_request(url)
    try:
        name = soup.find('div', {'class': 'event-titles'}
                         ).find_next('h1').decode_contents()
    except:
        name = soup.find('div', {'class': 'event-info'}
                         ).find_next('h1').decode_contents()
    try:
        # date = soup.find('div', {'class': 'event-titles'}).find_next('h4').decode_contents().split('<')[0]
        date = soup.find('div', {'class': 'event-titles'}
                         ).find_next('strong').decode_contents().split('on')[1]

        date = date.split('.')[0]

        date = parser.parse(date).strftime('%Y-%m-%d')
    except:

        date = soup.find('span', {'class': 'event-dates'}
                         ).decode_contents().split('|')[0]

        date = parser.parse(date).strftime('%Y-%m-%d')
    try:
        venue = soup.find('span', {'class': 'event-city'}).decode_contents()
        name = name + " {} ".format(venue)
    except:
        pass
    return name, date


def check_etix(url):
    soup = make_request(url)
    name = soup.find('h1', {'itemprop': 'name'}).text.strip()

    date = soup.find('div', {'class': 'time'})
    date = date.find('meta', {'itemprop': 'startDate'})['content']
    date = parser.parse(date).strftime('%Y-%m-%d')

    venue = soup.find('div', {'class': 'location'}).text.strip()
    name = name + " " + venue
    return name, date


def check_frontgate(url):
    soup = make_request(url)
    try:
        name = soup.find('meta', {'property': 'og:title'})['content']
    except:
        name = soup.find('meta', {'property': 'og:site_name'})['content']

    date = soup.find('div', {'class': 'date'}).text.strip().split('-')[0]
    date = date.split('\n')[0]
    date = parser.parse(date).strftime('%Y-%m-%d')

    venue = soup.find('div', {'class': 'venue'}).text.replace('at', '').strip()
    adr = soup.find('div', {'class': 'address'}).text.strip()
    adr = adr.split(',')
    adr = ','.join(adr[-2:])
    name = name + " " + venue + " " + adr

    return name, date


def check_ticketweb(url):
    url = url.split("?")[0]
    soup = make_request(url)
    try:
        name = soup.find('h1', {'class': 'title'}).find(
            'span', {'class': 'big'}).text.strip()
    except:
        name = soup.find('h1', {'class': 'title mttext-ellipsis mttext-ellipsis-3'}).find(
            'span', {'class': 'big'}).text.strip()

    date = soup.find(
        'div', {'class': 'info-item info-time'}).find('h4').text.strip()
    date = parser.parse(date).strftime('%Y-%m-%d')

    venue = soup.find(
        'a', {'href': '#', 'data-ng-click': "visible()", 'class': 'theme-title'})
    adr = venue.find_next('span').find_next('span').text.strip()
    venue = venue.text.strip()

    name = name + " " + venue + " " + adr

    return name, date


def check_seetickets(url):
    soup = make_request(url)
    time.sleep(2)
    # try:
    name = soup.find('h1', {'class': 'event-h2'}).text.strip()

    venue = soup.find('p', {'class': 'float-r'}
                      ).find_next('h5').decode_contents()
    adr = soup.find('input', {'type': 'hidden', 'id': 'locationaddress'})[
        'value']

    name = name + " " + venue + " " + adr
    # except:
    #     name = soup.find('title').text.strip()
    #     name = name.split('Buy Tickets to')
    # print(name)
    # time.sleep(3000)
    date = soup.find('time', {'itemprop': 'startDate'})['datetime']
    date = parser.parse(date).strftime('%Y-%m-%d')

    return name, date


def check_showclix(url):
    soup = make_request(url)
    name = soup.find('h1', {'class': 'showtitle'}).text.strip()

    date = soup.find('div', {'class': 'event_date'}).text.strip()
    date = parser.parse(date.split('-')[0]).strftime('%Y-%m-%d')

    venue = soup.find('span', {'class': 'venuename'}).text.strip()
    adr = soup.find('span', {'class': 'venuename'}).find_next(
        'span').find_next('span').text.strip()

    name = name + " " + venue + " " + adr
    return name, date


def check_prekindle(url):
    soup = make_request(url)
    name = soup.find('div', {'class': 'content-title'}
                     ).find_next('span').text.strip()
    try:
        date = parser.parse(soup.find('title').text.strip().split(',')[
                            2].split('|')[0]).strftime('%Y-%m-%d')
    except:
        date = parser.parse(soup.select_one(
            'div.content-info > div:nth-child(2) > div:nth-child(2)').text).strftime('%Y-%m-%d')
    # print(date)
    # time.sleep(3000)

    # location and address missing

    return name, date


def check_tixr(url):
    soup = make_request(url)
    name = soup.find('title').text.strip()
    try:
        date = parser.parse(soup.find('meta', {'property': 'event:start_time'})[
                            "content"]).strftime('%Y-%m-%d')
    except:
        pass

    return name, date


def check_tix24(url):
    soup = make_request(url)
    name = soup.find('title').text.strip()
    try:
        date = parser.parse(soup.find('meta', {'itemprop': 'startDate'})[
                            "content"]).strftime('%Y-%m-%d')
    except:
        pass

    return name, date


def check_admitone(url):
    soup = make_request(url)
    try:
        name = soup.find(
            'div', {'class': 'SingleEvent_sep_event_title__e6eS4'}).text.strip()
    except:
        try:
            name = soup.find('h1', {'class': 'showtitle'}).text.strip()
        except:
            print("this is another speical type")
            pass

    try:
        date = parser.parse(soup.find(
            'p', {'class': 'SingleEvent_sep_text_after_icon__erTt4'}).text.strip()).strftime('%Y-%m-%d')
    except:
        try:
            date = parser.parse(
                soup.find('div', {'class': 'event_date'}).text.strip()).strftime('%Y-%m-%d')
        except:
            pass

    return name, date
