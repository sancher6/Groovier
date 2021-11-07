import urllib.request
import urllib.parse
import re
import json

def concat_args(args): 
    response = ""
    for i, arg in enumerate(args): 
        if i > 0: 
            response = response + " " + arg
        else: 
            response = arg
    return response

def get_videoid(args):
    search = urllib.parse.quote(args)

    html = urllib.request.urlopen(
        f"https://www.youtube.com/results?search_query={search}"
    )
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

    if len(video_ids) == 0: 
        return ""
    else:
        return video_ids[0]

def get_song_title(video_id):
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % video_id}
    url = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        song_info = json.loads(response_text.decode())
        return song_info['title']