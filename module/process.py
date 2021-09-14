from module.db import Database
import module.ibm_watson_stt as stt
import datetime
def process_transcript(videoUUID: str, soundUUID: str):
  db = Database()
  queryObj = { "videoUUID" : videoUUID }
  db.update( queryObj,{ "latestUpdate": datetime.datetime.today().isoformat() ,"status" : "processing_transcript" } )
  print("processing through transcript...\n")
  sttResult = stt.get_transcript(soundUUID)
  updateObj = sttResult
  updateResult = db.update(queryObj,updateObj)
  db.update(queryObj, {"latestUpdate": datetime.datetime.today().isoformat()})
  db.close()
  return updateResult
