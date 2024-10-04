import questionary
from datetime import datetime
import requests
from yt_dlp import YoutubeDL

def human_format(num: int) -> str:
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def date_format(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') # YYYY-MM-DD

username = questionary.text("Enter your username Nimo TV:").ask().lower()

infoRequest = requests.get(f"https://api-cf.nimo.tv/oversea/nimo/api/v1/personalPage/personalPageForWeb/0/VN/1033/1066/100/{username}?keyType=100&body=eyJyZXF1ZXN0U291cmNlIjoiV0VCIn0")

info = infoRequest.json()
anchorId = info["data"]["result"]["anchorId"]

if info["code"] != 200:
  print(info["message"])
  exit()


data = {
  "keyType": "2",
  "body": "720090FE385A2AB138179E4C0E2284812A5E9FF765A08CBD587058546AE2319FB9B8A6C3B4C5B03398B5328912CDA951C3A9282C5A4B3E7C9F28B0B1A44498A4B5D50AE63A465E8CA1EBE93FBE89BA2D68BE51494E1AE551B2A42A88643E7494B56F21A411BFA3E71F8C89112350BE4A447835ED0669D4887264C933643564FBABC5BBECE7B6D97F0B48BE09A498906BE6A2601A2D42C7E68E647C1973583EA6E176D534F7FF0825E53BFF020E8AC0F9"
}

videoRequest = requests.post(f"https://video.nimo.tv/v1/liveVideo/aggregateVideos/1033/{anchorId}/5",data=data) # multipart/form-data

videoRes = videoRequest.json()

if videoRes["code"] != 200:
  print(videoRes["message"])
  exit()

replays = videoRes["data"]["result"]["aggregateVideoLists"][0]["liveVideoViewList"]



datas = []

for replay in replays:
  order = replays.index(replay) + 1
  id = replay["id"]
  title = replay["title"]
  avatar = replay["authorAvatarUrl"]
  author = replay["author"]
  views = human_format(replay["playNum"])
  duration = "{:.2f} minutes".format(replay["playDuration"] / 60)  # minutes
  thumbnail = replay["shareScreenshot"]
  sources = replay["multiResolutionVideoUrl"]
  createdDate = date_format(replay["createdTime"]/1000)
  
  item = {
    "order": order,
    "id": id,
    "title": title,
    "author": author,
    "views": views,
    "duration": duration,
    "thumbnail": thumbnail,
    "sources": sources,
    "createdDate": createdDate
  }
  datas.append(item)


selectVideo = questionary.select("Select video to download:", choices=[f"{data['order']}. {data['title']} - {data["author"]} - {data["duration"]} ({data['createdDate']})" for data in datas]).ask()
  
idxVideo = int(selectVideo.split(".")[0]) - 1

video = datas[idxVideo]

selectSource = questionary.select("Select video source:", choices=[f"{video["sources"].index(source) + 1}. {source['resolution']} - {source['videoUrl']}" for source in video["sources"]]).ask()

idxSource = int(selectSource.split(".")[0]) - 1

source = video["sources"][idxSource]

dir = questionary.text("Enter directory to save video or leave it blank to save in current directory:").ask()

YoutubeDL(params={
  "outtmpl": f"{dir}\\{video['title']} - {video['author']} - {source["resolution"]} ({video['createdDate']}).mp4",
}).download([source["videoUrl"]]) 





