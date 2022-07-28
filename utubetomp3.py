import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
import pytube
from pytube import YouTube
import os
import pydub
from pydub import AudioSegment
from tqdm import tqdm
import argparse


# Create the parser
parser = argparse.ArgumentParser('''\nRun the script as follows :-\n\tpython utubetomp3.py -u [Playlist_URL] \n\nOptional arguments :-\n\n\t-v : 1,if you want to download single video\n\t-m : 1,if you want to merge all the downloaded files\n\n\t''')# Add an argument
# parser = argparse.ArgumentParser()
parser.add_argument('-v',type=int,default=0) #if link is of video , if you want to download audio of a single video  ||v=video
parser.add_argument('-u', type=str, required=True)# url of the playlist or video                                     ||u=URL   
parser.add_argument('-m',type=int,default=0) #if you want to merge all the audios                                    ||m=merge
args = parser.parse_args()




def concatenate_audio_pydub(audio_clip_paths, output_path, verbose=1):
    """
    Concatenates two or more audio files into one audio file using PyDub library
    and save it to `output_path`. A lot of extensions are supported, more on PyDub's doc.
    """
    def get_file_extension(filename):
        """A helper function to get a file's extension"""
        return os.path.splitext(filename)[1].lstrip(".")

    clips = []
    # wrap the audio clip paths with tqdm if verbose
    audio_clip_paths = tqdm(audio_clip_paths, "Reading audio file") if verbose else audio_clip_paths
    for clip_path in audio_clip_paths:
        # get extension of the audio file
        extension = get_file_extension(clip_path)
        # load the audio clip and append it to our list
        clip = AudioSegment.from_file(clip_path, extension)
        clips.append(clip)

    final_clip = clips[0]
    range_loop = tqdm(list(range(1, len(clips))), "Concatenating audio") if verbose else range(1, len(clips))
    for i in range_loop:
        # looping on all audio files and concatenating them together
        # ofc order is important
        final_clip = final_clip + clips[i]
    # export the final clip
    final_clip_extension = get_file_extension(output_path)
    if verbose:
        print(f"Exporting resulting audio file to {output_path}")
    final_clip.export(output_path, format=final_clip_extension)

#extract playlist id from url
# this is the url of the playlist
url=str(args.u)
links=[]
file_names=[]

if args.v:
    links.append(url)
else:
    # developerKey=str(input("Enter Your developer Api [read README to know more about developer API]"))
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]
    print(f'get all playlist items links from {playlist_id}')
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="AIzaSyA-1zmN-pL48Pc2siHSD-OkJ-4Tyiqqals")

    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    print(f"total: {len(playlist_items)}")
    links=[ 
        f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s'
        for t in playlist_items
    ]
   



for link in links:
    
    try:
        yt = YouTube(str(link))
        
        video = yt.streams.filter(only_audio=True).first()
        # print("Enter the destination address (leave blank to save in current directory)")
        # destination = str(input(" ")) or '.'
        print("Downloading - ",yt.title,"\n")
        destination = '.'
        out_file = video.download(output_path=destination)
        base1, ext = os.path.splitext(out_file)
        
        file_names.append(out_file)
    
    except:
        print("An Error occured while downloading ....Retrying ! ")



print("Completed-Downloading") 

if args.m:
    print("Merging all the files . . .\n")
    print("       ||      \n")
    print("       ||      \n")
    print("       ||      \n")
    print("       \/      \n")
    print("Make sure to Rename combined.mp3 to file overriding       \n")

    concatenate_audio_pydub(file_names,'./combined.mp3',1)










