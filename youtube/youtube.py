from googleapiclient.discovery import build
import pandas as pd
import json
from datetime import datetime


class Youtube:
    def __init__(self, dev_key, channelId, data_path="./data"):
        self.youtube = build('youtube', 'v3', developerKey=dev_key)
        self.channelId = channelId
        self.data_path = data_path

    def get_playlists(self):
        playlists = self.youtube.playlists().list(
            channelId=self.channelId,
            part='snippet',
            maxResults=20
        ).execute()

        ids = []
        titles = []
        for i in playlists['items']:
            ids.append(i['id'])
            titles.append(i['snippet']['title'])

        df = pd.DataFrame([titles, ids]).T
        df.columns = ['Title', 'ID']

        return df

    def get_playlist_videos(self, playlistId):
        playlist_videos = self.youtube.playlistItems().list(
            playlistId=playlistId,
            part='snippet',
            maxResults=80
        ).execute()

        names = []
        ids = []
        dates = []

        for v in playlist_videos['items']:
            names.append(v['snippet']['title'])
            ids.append(v['snippet']['resourceId']['videoId'])
            dates.append(v['snippet']['publishedAt'])

        df = pd.DataFrame([dates, names, ids]).T
        df.columns = ['Date', 'Title', 'ID']

        return df

    def get_video_info(self, videoId):
        videoInfo = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=videoId).execute()

        try:
            return (videoInfo['items'][0]['snippet']['title'],
                    videoInfo['items'][0]['snippet']['description'],
                    videoInfo['items'][0]['snippet']['thumbnails'][list(videoInfo['items'][0]['snippet']['thumbnails'].keys())[-1]]['url'],
                    videoInfo['items'][0]['snippet']['publishedAt'])
        except:
            return None, None, None, None

    def get_new_videos(self):
        res = []
        playlists = self.get_playlists()

        with open(self.data_path + "/data.json") as f:
            json_data = json.load(f)

        last_update = datetime.strptime(json_data["archive_last_update"], '%Y-%m-%dT%H:%M:%SZ')
        max_date = datetime.min

        # for each playlists, get video list
        for i in range(len(playlists)):
            playlist_id = playlists.iloc[i]['ID']
            videos = self.get_playlist_videos(playlist_id)

            # for each video, get info and append it to result
            for j in range(len(videos)):
                date_dt = datetime.strptime(videos.iloc[j]['Date'], '%Y-%m-%dT%H:%M:%SZ')
                video_id = videos.iloc[j]['ID']

                # update max date
                if date_dt > max_date:
                    max_date = date_dt

                # if video is old then last update, continue
                if date_dt <= last_update:
                    continue

                info = self.get_video_info(video_id)

                if info[0] is None:
                    continue

                title, description, thumbnail, date = info

                video = {
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "thumbnail": thumbnail,
                    "playlist": playlists.iloc[i]['Title'],
                    "date": date
                }

                res.append(video)

        # if max date is sooner than last update, update the date
        if last_update < max_date:
            json_data["archive_last_update"] = max_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            with open(self.data_path + "/data.json", 'w') as f:
                json.dump(json_data, f, indent=4)

        return res
