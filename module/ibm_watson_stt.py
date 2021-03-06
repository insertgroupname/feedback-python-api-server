from dotenv import load_dotenv
load_dotenv()

def get_transcript(audio_name: str):
    print(f"into transcript\n")
    import os, io
    import json
    import logging, traceback
    
    from ibm_watson import SpeechToTextV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    

    authenticator = IAMAuthenticator(os.environ['IBM_API_KEY'])
    speech_to_text = SpeechToTextV1(
        authenticator=authenticator
    )
    print("got token")
    url = os.environ["IBM_URL_STT"]
    speech_to_text.set_service_url(url)
    print("set url")
    ext = audio_name.split(".")[1]
    with io.open( os.path.join( "upload/audio", audio_name ), "rb" ) as audio_file:
        print("transforming")
        output = speech_to_text.recognize(
            audio_file, 
            content_type='audio/'+ext,
            model='en-US_NarrowbandModel',
            word_confidence=True,
            timestamps=True,
        )
        transcriptObj= {}
        try:
            with open( os.path.join( "transcript", "{}.json".format(audio_name.split(".")[0]) ), "w" ) as file:
                lists = []
                for result in output.result['results']:
                    for alt in result['alternatives']:
                        lists.append(dict({
                                'transcript': alt['transcript'], 
                                'confidence': alt['confidence'], 
                                'timestamps': alt['timestamps'],
                                'word_confidence': alt['word_confidence'],
                            }))
                transcriptObj = dict( { 'results':lists } )
                json.dump( transcriptObj , file, indent=4 )
		        
        except Exception as e:
            logging.error(traceback.format_exc())
        finally:
            print("transcript done\n")
            return transcriptObj
