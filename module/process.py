from logging import error
from module.db import Database
import module.ibm_watson_stt as stt
import datetime


def process_transcript(videoUUID: str, soundUUID: str):
    try:
        db = Database()
        queryObj = {"videoUUID": videoUUID}
        db.update(queryObj, {"lastUpdate": datetime.datetime.today(
        ).isoformat(), "status": "processing_transcript"})
    except (error):
        print(error)

    print("processing through transcript...\n")
    sttResult = stt.get_transcript(soundUUID)
    updateResult = db.update(
        queryObj, {'report.transcript': sttResult["results"]})
    db.update(
        queryObj, {"lastUpdate": datetime.datetime.today().isoformat()})
    db.close()
    return updateResult
