﻿# -*- coding: utf-8 -*-
"""
A Kodi plugin for Viaplay
"""
import sys
import os
import urllib
import urlparse
from datetime import datetime
import time

import dateutil.parser
from dateutil import tz
from resources.lib.vialib import vialib

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import xbmcplugin

addon = xbmcaddon.Addon()
addon_path = xbmc.translatePath(addon.getAddonInfo('path'))
addon_profile = xbmc.translatePath(addon.getAddonInfo('profile'))
tempdir = os.path.join(addon_profile, 'tmp')
language = addon.getLocalizedString
logging_prefix = '[%s-%s]' % (addon.getAddonInfo('id'), addon.getAddonInfo('version'))

if not xbmcvfs.exists(addon_profile):
    xbmcvfs.mkdir(addon_profile)
if not xbmcvfs.exists(tempdir):
    xbmcvfs.mkdir(tempdir)

_url = sys.argv[0]  # get the plugin url in plugin:// notation.
_handle = int(sys.argv[1])  # get the plugin handle as an integer number

username = addon.getSetting('email')
password = addon.getSetting('password')
cookie_file = os.path.join(addon_profile, 'cookie_file')
deviceid_file = os.path.join(addon_profile, 'deviceId')

if addon.getSetting('ssl') == 'false':
    disable_ssl = False
else:
    disable_ssl = True

if addon.getSetting('debug') == 'false':
    debug = False
else:
    debug = True

if addon.getSetting('subtitles') == 'false':
    subtitles = False
else:
    subtitles = True

if addon.getSetting('country') == '0':
    country = 'se'
elif addon.getSetting('country') == '1':
    country = 'dk'
elif addon.getSetting('country') == '2':
    country = 'no'
else:
    country = 'fi'

vp = vialib(username, password, cookie_file, deviceid_file, tempdir, country, disable_ssl, debug)


def addon_log(string):
    if debug:
        xbmc.log("%s: %s" % (logging_prefix, string))


def display_auth_message(error):
    if error.value == 'UserNotAuthorizedForContentError':
        message = language(30020)
    elif error.value == 'PurchaseConfirmationRequiredError':
        message = language(30021)
    elif error.value == 'UserNotAuthorizedRegionBlockedError':
        message = language(30022)
    else:
        message = error.value
    dialog = xbmcgui.Dialog()
    dialog.ok(language(30017), message)


def root_menu():
    categories = vp.get_categories(input=vp.base_data, method='data')
    listing = []

    for category in categories:
        categorytype = category['type']
        videotype = category['name']
        title = category['title']
        if categorytype == 'vod':
            list_item = xbmcgui.ListItem(label=title)
            list_item.setProperty('IsPlayable', 'false')
            list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
            list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
            if videotype == 'series':
                parameters = {'action': 'series', 'url': category['href']}
            elif videotype == 'movie' or videotype == 'rental':
                parameters = {'action': 'movie', 'url': category['href']}
            elif videotype == 'sport':
                parameters = {'action': 'sport', 'url': category['href']}
            elif videotype == 'kids':
                parameters = {'action': 'kids', 'url': category['href']}
            else:
                addon_log('Unsupported videotype found: %s' % videotype)
                parameters = {'action': 'showmessage', 'message': 'This type (%s) is not yet supported.' % videotype}
            recursive_url = _url + '?' + urllib.urlencode(parameters)
            is_folder = True
            listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    list_search()
    xbmcplugin.endOfDirectory(_handle)


def movie_menu(url):
    categories = vp.get_categories(url)
    listing = []

    for category in categories:
        title = category['title']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'sortby', 'url': category['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def series_menu(url):
    categories = vp.get_categories(url)
    listing = []

    for category in categories:
        title = category['title']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'sortby', 'url': category['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def kids_menu(url):
    categories = vp.get_categories(url)
    listing = []

    for category in categories:
        title = '%s: %s' % (category['group']['title'].title(), category['title'])
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'listproducts', 'url': category['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def sort_by(url):
    sortings = vp.get_sortings(url)
    listing = []

    for sorting in sortings:
        title = sorting['title']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        try:
            if sorting['id'] == 'alphabetical':
                parameters = {'action': 'listalphabetical', 'url': sorting['href']}
            else:
                parameters = {'action': 'listproducts', 'url': sorting['href']}
        except TypeError:
            parameters = {'action': 'listproducts', 'url': sorting['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))

    list_products_alphabetical(url)
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def list_products_alphabetical(url):
    """List all products in alphabetical order."""
    list_item = xbmcgui.ListItem(label=language(30013))
    list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
    list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
    parameters = {'action': 'listproducts', 'url': url + '?sort=alphabetical'}
    recursive_url = _url + '?' + urllib.urlencode(parameters)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, recursive_url, list_item, is_folder)


def alphabetical_menu(url):
    letters = vp.get_letters(url)
    listing = []

    for letter in letters:
        title = letter.encode('utf-8')
        if letter == '0-9':
            # 0-9 needs to be sent as a pound-sign
            letter = '#'
        else:
            letter = title.lower()
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'listproducts', 'url': url + '&letter=' + urllib.quote(letter)}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def list_next_page(data):
    """Return a 'next page item' if the current page is less than the total page count."""
    try:
        currentPage = data['_embedded']['viaplay:blocks'][0]['currentPage']
        pageCount = data['_embedded']['viaplay:blocks'][0]['pageCount']
    except KeyError:
        currentPage = data['currentPage']
        pageCount = data['pageCount']
    if pageCount > currentPage:
        try:
            url = data['_embedded']['viaplay:blocks'][0]['_links']['next']['href']
        except KeyError:
            url = data['_links']['next']['href']

        list_item = xbmcgui.ListItem(label=language(30018))
        parameters = {'action': 'nextpage', 'url': url}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, recursive_url, list_item, is_folder)


def list_products(url, *display):
    data = vp.make_request(url=url, method='get')
    products = vp.get_products(input=data, method='data')
    listing = []
    sort = None

    for item in products:
        type = item['type']
        try:
            playid = item['system']['guid']
            streamtype = 'guid'
        except KeyError:
            """The guid is not always available from the category listing.
            Send the self URL and let play_video grab the guid from there instead
            as it always provides more detailed data about each product."""
            playid = item['_links']['self']['href']
            streamtype = 'url'
        parameters = {'action': 'play', 'playid': playid.encode('utf-8'), 'streamtype': streamtype}
        recursive_url = _url + '?' + urllib.urlencode(parameters)

        if type == 'episode':
            title = item['content']['series']['episodeTitle']
            is_folder = False
            is_playable = 'true'
            list_item = xbmcgui.ListItem(label=title)
            list_item.setProperty('IsPlayable', is_playable)
            list_item.setInfo('video', item_information(item))
            list_item.setArt(art(item))
            listing.append((recursive_url, list_item, is_folder))

        if type == 'sport':
            local_tz = tz.tzlocal()
            startdate_utc = dateutil.parser.parse(item['epg']['start'])
            startdate_local = startdate_utc.astimezone(local_tz)
            status = vp.get_sports_status(item)
            if status == 'archive':
                title = 'Archive: %s' % item['content']['title'].encode('utf-8')
                is_playable = 'true'
            else:
                title = '%s (%s)' % (item['content']['title'].encode('utf-8'), startdate_local.strftime("%H:%M"))
                is_playable = 'true'
            if status == 'upcoming':
                parameters = {'action': 'showmessage',
                              'message': '%s %s.' % (language(30016), startdate_local.strftime("%Y-%m-%d %H:%M"))}
                recursive_url = _url + '?' + urllib.urlencode(parameters)
                is_playable = 'false'
            is_folder = False
            list_item = xbmcgui.ListItem(label=title)
            list_item.setProperty('IsPlayable', is_playable)
            list_item.setInfo('video', item_information(item))
            list_item.setArt(art(item))
            if 'live' in display:
                if status == 'live':
                    listing.append((recursive_url, list_item, is_folder))
            elif 'upcoming' in display:
                if status == 'upcoming':
                    listing.append((recursive_url, list_item, is_folder))
            elif 'archive' in display:
                if status == 'archive':
                    listing.append((recursive_url, list_item, is_folder))
            else:
                listing.append((recursive_url, list_item, is_folder))

        elif type == 'movie':
            title = '%s (%s)' % (item['content']['title'].encode('utf-8'), str(item['content']['production']['year']))
            if item['system']['availability']['planInfo']['isRental'] is True:
                title = title + ' *'  # mark rental products with an asterisk
            is_folder = False
            is_playable = 'true'
            list_item = xbmcgui.ListItem(label=title)
            list_item.setProperty('IsPlayable', is_playable)
            list_item.setInfo('video', item_information(item))
            list_item.setArt(art(item))
            listing.append((recursive_url, list_item, is_folder))

        elif type == 'series':
            title = item['content']['series']['title'].encode('utf-8')
            self_url = item['_links']['viaplay:page']['href']
            parameters = {'action': 'seasons', 'url': self_url}
            recursive_url = _url + '?' + urllib.urlencode(parameters)
            is_folder = True
            is_playable = 'false'
            list_item = xbmcgui.ListItem(label=title)
            list_item.setProperty('IsPlayable', is_playable)
            list_item.setInfo('video', item_information(item))
            list_item.setArt(art(item))
            listing.append((recursive_url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    if sort is True:
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    list_next_page(data)
    # xbmc.executebuiltin("Container.SetViewMode(500)") - force media view
    xbmcplugin.endOfDirectory(_handle)


def list_seasons(url):
    seasons = vp.get_seasons(url)
    listing = []
    for season in seasons:
        title = '%s %s' % (language(30014), season['title'])
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'listproducts', 'url': season['_links']['self']['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def item_information(item):
    """Return the product information in a xbmcgui.setInfo friendly dict.
    Supported content types: episode, series, movie, sport"""
    type = item['type']
    mediatype = None
    title = None
    tvshowtitle = None
    season = None
    episode = None
    plot = None
    director = None
    cast = []
    try:
        duration = int(item['content']['duration']['milliseconds']) / 1000
    except KeyError:
        duration = None
    try:
        imdb_code = item['content']['imdb']['id']
    except KeyError:
        imdb_code = None
    try:
        rating = float(item['content']['imdb']['rating'])
    except KeyError:
        rating = None
    try:
        votes = str(item['content']['imdb']['votes'])
    except KeyError:
        votes = None
    try:
        year = int(item['content']['production']['year'])
    except KeyError:
        year = None
    try:
        genres = []
        for genre in item['_links']['viaplay:genres']:
            genres.append(genre['title'])
        genre = ', '.join(genres)
    except KeyError:
        genre = None
    try:
        mpaa = item['content']['parentalRating']
    except KeyError:
        mpaa = None

    if type == 'episode':
        mediatype = 'episode'
        title = item['content']['series']['episodeTitle'].encode('utf-8')
        tvshowtitle = item['content']['series']['title'].encode('utf-8')
        season = int(item['content']['series']['season']['seasonNumber'])
        episode = int(item['content']['series']['episodeNumber'])
        plot = item['content']['synopsis'].encode('utf-8')
        xbmcplugin.setContent(_handle, 'episodes')
    elif type == 'series':
        mediatype = 'tvshow'
        title = item['content']['series']['title'].encode('utf-8')
        tvshowtitle = item['content']['series']['title'].encode('utf-8')
        try:
            plot = item['content']['series']['synopsis'].encode('utf-8')
        except KeyError:
            plot = item['content']['synopsis'].encode('utf-8')  # needed for alphabetical listing
        xbmcplugin.setContent(_handle, 'tvshows')
    elif type == 'movie':
        mediatype = 'movie'
        title = item['content']['title'].encode('utf-8')
        plot = item['content']['synopsis'].encode('utf-8')
        try:
            for actor in item['content']['people']['actors']:
                cast.append(actor)
        except KeyError:
            pass
        try:
            directors = []
            for director in item['content']['people']['directors']:
                directors.append(director)
            director = ', '.join(directors)
        except KeyError:
            pass
        xbmcplugin.setContent(_handle, 'movies')
    elif type == 'sport':
        mediatype = 'video'
        title = item['content']['title'].encode('utf-8')
        plot = item['content']['synopsis'].encode('utf-8')
        xbmcplugin.setContent(_handle, 'episodes')
    info = {
        'mediatype': mediatype,
        'title': title,
        'tvshowtitle': tvshowtitle,
        'season': season,
        'episode': episode,
        'year': year,
        'plot': plot,
        'duration': duration,
        'code': imdb_code,
        'rating': rating,
        'votes': votes,
        'genre': genre,
        'director': director,
        'mpaa': mpaa,
        'cast': cast
    }
    return info


def art(item):
    """Return the available art in a xbmcgui.setArt friendly dict."""
    type = item['type']
    try:
        boxart = item['content']['images']['boxart']['url'].split('.jpg')[0] + '.jpg'
    except KeyError:
        boxart = None
    try:
        hero169 = item['content']['images']['hero169']['template'].split('.jpg')[0] + '.jpg'
    except KeyError:
        hero169 = None
    try:
        coverart23 = item['content']['images']['coverart23']['template'].split('.jpg')[0] + '.jpg'
    except KeyError:
        coverart23 = None
    try:
        coverart169 = item['content']['images']['coverart23']['template'].split('.jpg')[0] + '.jpg'
    except KeyError:
        coverart169 = None
    try:
        landscape = item['content']['images']['landscape']['url'].split('.jpg')[0] + '.jpg'
    except KeyError:
        landscape = None

    if type == 'episode' or type == 'sport':
        thumbnail = landscape
    else:
        thumbnail = boxart
    fanart = hero169
    banner = landscape
    cover = coverart23
    poster = boxart

    art = {
        'thumb': thumbnail,
        'fanart': fanart,
        'banner': banner,
        'cover': cover,
        'poster': poster
    }

    return art


def list_search():
    list_search = xbmcgui.ListItem(label=vp.base_data['_links']['viaplay:search']['title'])
    list_search.setArt({'icon': os.path.join(addon_path, 'icon.png')})
    list_search.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
    parameters = {'action': 'search', 'url': vp.base_data['_links']['viaplay:search']['href']}
    recursive_url = _url + '?' + urllib.urlencode(parameters)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, recursive_url, list_search, is_folder)


def get_userinput(title):
    query = None
    keyboard = xbmc.Keyboard('', title)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        addon_log('User input string: %s' % query)
    return query


def search(url):
    try:
        query = get_userinput(language(30015))
        if len(query) > 0:
            url = '%s?query=%s' % (url, urllib.quote(query))
            list_products(url)
    except TypeError:
        pass


def play_video(playid, streamtype):
    if streamtype == 'url':
        url = playid
        guid = vp.get_products(input=url, method='url')['system']['guid']
    else:
        guid = playid

    try:
        video_urls = vp.get_video_urls(guid)
    except vp.AuthFailure as error:
        video_urls = False
        display_auth_message(error)
    except vp.LoginFailure:
        video_urls = False
        dialog = xbmcgui.Dialog()
        dialog.ok(language(30005),
                  language(30006))

    if video_urls:
        play_item = xbmcgui.ListItem(path=video_urls['stream_url'])
        play_item.setProperty('IsPlayable', 'true')
        if subtitles:
            play_item.setSubtitles(vp.download_subtitles(video_urls['subtitle_urls']))
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def sports_menu(url):
    # URL is hardcoded for now as the sports date listing is not available on all platforms
    if country == 'fi':
        live_url = 'https://content.viaplay.fi/androiddash-fi/urheilu2'
    else:
        live_url = 'https://content.viaplay.%s/androiddash-%s/sport2' % (country, country)
    listing = []
    categories = vp.get_categories(live_url)
    now = datetime.now()

    for category in categories:
        date_object = datetime(
            *(time.strptime(category['date'], '%Y-%m-%d')[0:6]))  # http://forum.kodi.tv/showthread.php?tid=112916
        title = category['date']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        if date_object.date() == now.date():
            parameters = {'action': 'sportstoday', 'url': category['href']}
        else:
            parameters = {'action': 'listsports', 'url': category['href']}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def sports_today(url):
    types = ['live', 'upcoming', 'archive']
    listing = []
    for type in types:
        list_item = xbmcgui.ListItem(label=type.title())
        list_item.setProperty('IsPlayable', 'false')
        list_item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        list_item.setArt({'fanart': os.path.join(addon_path, 'fanart.jpg')})
        parameters = {'action': 'listsportstoday', 'url': url, 'display': type}
        recursive_url = _url + '?' + urllib.urlencode(parameters)
        is_folder = True
        listing.append((recursive_url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def router(paramstring):
    """Router function that calls other functions depending on the provided paramstring."""
    params = dict(urlparse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'movie':
            movie_menu(params['url'])
        elif params['action'] == 'kids':
            kids_menu(params['url'])
        elif params['action'] == 'series':
            series_menu(params['url'])
        elif params['action'] == 'sport':
            sports_menu(params['url'])
        elif params['action'] == 'seasons':
            list_seasons(params['url'])
        elif params['action'] == 'nextpage':
            list_products(params['url'])
        elif params['action'] == 'listsports':
            list_products(params['url'])
        elif params['action'] == 'sportstoday':
            sports_today(params['url'])
        elif params['action'] == 'listsportstoday':
            list_products(params['url'], params['display'])
        elif params['action'] == 'play':
            play_video(params['playid'], params['streamtype'])
        elif params['action'] == 'sortby':
            sort_by(params['url'])
        elif params['action'] == 'listproducts':
            list_products(params['url'])
        elif params['action'] == 'listalphabetical':
            alphabetical_menu(params['url'])
        elif params['action'] == 'search':
            search(params['url'])
        elif params['action'] == 'showmessage':
            dialog = xbmcgui.Dialog()
            dialog.ok(language(30017),
                      params['message'])
    else:
        root_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:])  # trim the leading '?' from the plugin call paramstring
