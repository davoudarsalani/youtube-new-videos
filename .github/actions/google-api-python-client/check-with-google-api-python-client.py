#!/usr/bin/env python

## this is a slightly modified version of jadi.py in davoudarsalani/scripts repository

from functools import partial
from getopt import getopt
from subprocess import run
from sys import argv
from urllib.request import urlopen

from googleapiclient.discovery import build
from youtube_dl import YoutubeDL


def getopts() -> None:
    global count_last, channel_id, last_file, titles_file, api_key

    try:
        duos, duos_long = getopt(
            script_args,
            'l:c:f:t:a:',
            ['count-last=', 'channel-id=', 'last-file=', 'titles-file=', 'api-key='],
        )
    except Exception as exc:
        print(f'ERROR: {exc!r}')
        exit(1)

    for opt, arg in duos:
        if opt in ('-l', '--count-last'):
            count_last = int(arg)
        elif opt in ('-c', '--channel-id'):
            channel_id = arg
        elif opt in ('-f', '--last-file'):
            last_file = arg
        elif opt in ('-t', '--titles-file'):
            titles_file = arg
        elif opt in ('-a', '--api-key'):
            api_key = arg


def main():
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

            ## download gp.py to use convert_second function (borrowed from download.py script)
            gp_response = urlopen('https://raw.githubusercontent.com/davoudarsalani/scripts/master/gp.py')
            with open(f'./.github/actions/google-api-python-client/gp.py', 'wb') as opened_gp:
                for chunk in iter(partial(gp_response.read, 8192), b''):  ## 8192 is 8KB
                    opened_gp.write(chunk)
            ## now a sloppy trick to remove everything other than convert_second function to prevent ModuleNotFoundError:
            ## step 1: remove everythin before pattern
            run("sed -i -n '/^def convert_second/,$p' ./.github/actions/google-api-python-client/gp.py", shell=True)
            ## step 2: remove everything after pattern (2,$ means ignore the first occurrence)
            ##         (had to put the commad inside {} to prevent the error: sed: -e expression #1, char 4: unknown command: `/')
            ##         (https://stackoverflow.com/questions/6869449/skipping-the-first-n-lines-when-using-regex-with-sed)
            run("sed -i '2,${ /^def /,$d }' ./.github/actions/google-api-python-client/gp.py", shell=True)
            ## now we can import
            from gp import convert_second

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
                        vid_duration = video_obj['duration']  ## 41
                        vid_duration = convert_second(vid_duration)  ## 00:00:41

                        message_text = f'{message_text}{title}\n{vid_duration}\n{u}\n\n'

                ## write info to titles_file
                message_text = f'{message_text.strip()}\n'
                with open(titles_file, 'w') as opened_titles_file:
                    opened_titles_file.write(message_text)

            except Exception as exc:
                print(f'ERROR: {exc!r}')

    except Exception as exc:
        print(f'ERROR: {exc!r}')


if __name__ == '__main__':
    script_args = argv[1:]
    message_text = ''
    urls = []

    main()
