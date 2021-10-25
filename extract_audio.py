import moviepy.editor as mp

def extractor(videoUUID):
    path = "upload/"
    try:
        video = mp.VideoFileClip(path+"video/"+videoUUID)
        # output_filename = videoUUID.split(".")[0] + ".wav"
        output_filename_ogg = videoUUID.split(".")[0] + ".ogg"
        video.audio.write_audiofile(f"{path}audio/{output_filename_ogg}")
        # video.audio.write_audiofile(f"{path}audio/{output_filename}")
    except Exception as e:
        print(e)
    return output_filename_ogg
