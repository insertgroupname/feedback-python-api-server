from module.db import Database
import module.ibm_watson_stt as stt

def process_transcript(videoUUID: str, soundUUID: str):
  print("processing through transcript...\n")
  sttResult = stt.get_transcript(soundUUID)
  db = Database()
  queryObj = { "videoUUID" : videoUUID }
  updateObj = sttResult
  updateResult = db.update(queryObj,updateObj)
  db.update( queryObj,{ "status" : "done" } )
  return updateResult
