from typing import final
from flask import (
    Flask,
    request,
    render_template,
)
import requests
from extract_audio import extractor
from module.process import process_transcript
from module.nlp import process_nlp

app = Flask(__name__)


# @app.route("/")
# def index():
#     return "Hello world"


@app.route("/convert_sound", methods=["POST"])
def convert_sound():
    errors = []
    videoUUID = ""
    soundUUID = ""
    try:
        videoUUID = request.args.get("file_name")
        soundUUID = extractor(videoUUID)
    except:
        errors.append("Unable to get URL. Please make sure it's valid and try again.")
    # finally:
    #     filename = request.args.get("file_name")
    #     sound_ = extractor(filename)
    process_transcript(videoUUID, soundUUID)
    nlp_res = process_nlp(videoUUID)
    return f"result modified "


if __name__ == "__main__":
    app.run()
