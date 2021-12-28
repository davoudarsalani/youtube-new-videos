#!/usr/bin/env python

## this is a slightly modified version of jadi.py in davoudarsalani/scripts repository

from getopt import getopt
from sys import argv

from googleapiclient.discovery import build
from youtube_dl import YoutubeDL

script_args = argv[1:]
message_text = ''
urls = []


def getopts() -> None:
    global count_last, channel_id, last_file, error_file, titles_file, api_key

    try:
        duos, duos_long = getopt(
            script_args,
            'l:c:f:e:t:a:',
            [
                'count-last=',
                'channel-id=',
                'last-file=',
                'error-file=',
                'titles-file=',
                'api-key=',
            ],
        )
    except Exception as exc:
        save_error(f'{exc!r}')
        exit()

    for opt, arg in duos:
        if opt in ('-l', '--count-last'):
            count_last = int(arg)
        elif opt in ('-c', '--channel-id'):
            channel_id = arg
        elif opt in ('-f', '--last-file'):
            last_file = arg
        elif opt in ('-e', '--error-file'):
            error_file = arg
        elif opt in ('-t', '--titles-file'):
            titles_file = arg
        elif opt in ('-a', '--api-key'):
            api_key = arg


def save_error(text):
    with open(error_file, 'w') as opened_error_file:
        opened_error_file.write(text)


def convert_duration(seconds: int) -> str:
    seconds = int(seconds)
    ss = f'{int(seconds % 60):02}'
    mm = f'{int(seconds / 60 % 60):02}'
    hh = f'{int(seconds / 3600 % 24):02}'

    return f'{hh}:{mm}:{ss}'


getopts()

try:
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(part='statistics', id=channel_id)
    response = request.execute()
    count = int(response['items'][0]['statistics']['videoCount'])

    ## get new count
    ## already got in try

    ## save count as last to compare in our next read
    with open(last_file, 'w') as opened_last_file:
        opened_last_file.write(f'{str(count)}\n')

    ## compare
    diff = count - count_last
    if diff > 0:

        ## get urls
        try:
            request = youtube.search().list(part='snippet', order='date', channelId=channel_id)
            response = request.execute()

            videos = response['items']

            for i in range(diff):
                video = videos[i]
                url = video['id']['videoId']
                url = f'https://www.youtube.com/watch?v={url}'
                urls.append(url)

            ## googleapiclient only gives us title and url
            ## so for duration we have to use youtube_dl

            # tor_proxy = 'socks5://127.0.0.1:9050'
            options = {
                # 'proxy': tor_proxy,
                'no_color': True,
                'skip_download': True,
            }

            ## get title and duration
            for u in urls:
                with YoutubeDL(options) as opened_youtubedl:
                    # opened_youtubedl.cache.remove()
                    video_obj = opened_youtubedl.extract_info(u, download=False)
                    title = video_obj['title']
                    duration = video_obj['duration']  ## 41
                    duration = convert_duration(duration)  ## 00:00:41

                    message_text = f'{message_text}{title}\n{duration}\n{u}\n\n'

            ## write info to titles_file
            message_text = f'{message_text.strip()}\n'
            with open(titles_file, 'w') as opened_titles_file:
                opened_titles_file.write(message_text)

        except Exception as exc:
            ## save error
            save_error(f'{exc!r}')

except Exception as exc:
    ## save error
    save_error(f'{exc!r}')
