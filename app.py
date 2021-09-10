from typing import final
from flask import (
    Flask,
    request,
    render_template,
)
import requests
from extract_audio import extractor

app = Flask(__name__)


# @app.route("/")
# def index():
#     return "Hello world"


@app.route("/convert_sound", methods=["POST"])
def convert_sound():
    errors = []
    filename = ""
    sound_ = ""
    try:
        filename = request.args.get("file_name")
        sound_ = extractor(filename)
    except:
        errors.append("Unable to get URL. Please make sure it's valid and try again.")
    # finally:
    #     filename = request.args.get("file_name")
    #     sound_ = extractor(filename)
    return f"filename is {sound_}"


@app.route("/nlp", methods=["POST"])
def nlp():
    errors = []
    try:
        pass
    except:
        errors.append()
    return "TBD"


if __name__ == "__main__":
    app.run()
