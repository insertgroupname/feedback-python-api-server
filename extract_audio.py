import moviepy.editor as mp


def extractor(filename):
    video = mp.VideoFileClip("filename")
    output_filename = filename.split(".")[0] + ".mp3"
    video.audio.write_audiofile(f"{output_filename}")
    return output_filename
