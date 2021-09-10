import moviepy.editor as mp
import os

def extractor(videoUUID):
    path = "../Feedback/upload/"
    try:
        video = mp.VideoFileClip(path+"video/"+videoUUID)
        output_filename = videoUUID.split(".")[0] + ".wav"
        video.audio.write_audiofile(f"{path}/audio/{output_filename}")
    except Exception as e:
        print(e)
    return output_filename