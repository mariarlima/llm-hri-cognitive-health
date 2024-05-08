import os
import logging
import datetime
import torch
import numpy as np
import whisper
import speech_recognition as sr
from playsound import playsound
from dotenv import load_dotenv
from openai import OpenAI
from unrealspeech import UnrealSpeechAPI, play, save

import faulthandler

faulthandler.enable()

is_using_voice = True
is_playback = False
whisper_model_id = "medium.en"
enable_LLM_module = True
enable_TTS_module = True
wav_path = 'output.wav'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8.8s] %(message)s",
    handlers=[logging.StreamHandler(),
              ],
)
#logging.FileHandler(f'log/{datetime.datetime.now().isoformat().replace(":", "-")}.log', encoding='utf-8')
logger = logging.getLogger('Default')

logger.info("Voice input is %r.", is_using_voice)
logger.info("Voice playback is %r.", is_playback)
logger.info("Using %s Whisper model.", whisper_model_id)
logger.info("LLM module is %r.", enable_LLM_module)
logger.info("TTS module is %r.", enable_TTS_module)

########## Initialization ##########
if torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info("PyTorch is using CUDA.")
else:
    device = "cpu"
    logger.warning("PyTorch is using CPU.")

whisper_model = whisper.load_model(whisper_model_id).to(device)

r = sr.Recognizer()
mic = sr.Microphone()
audio = None
# with mic as source:
#     r.adjust_for_ambient_noise(source)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=api_key)

api_key = os.getenv("UNREAL_SPEECH_KEY")
speech_api = UnrealSpeechAPI(api_key)

llm_prompt = [{"role": "system",
               "content": "You are Blossom, a robot that will interact in a picture description task based on the cookie theft picture. You should give hints and encourage while giving turns for the user to reply. Prompt the user with different areas of the picture that havent been mentioned."}]

while True:
    if is_using_voice:
        ########## Listen ##########
        with mic as source:
            r.adjust_for_ambient_noise(source)
            logger.info("listening...")
            audio = r.listen(source)

        audio_np_array = torch.from_numpy(
            np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)

        wav_path = 'output.wav'
        with open(wav_path, "wb") as f:
            f.write(audio.get_wav_data())

        # print(audio_np_array)
        if is_playback:
            logger.info("Start playback.")
            # Play the saved audio
            playsound(wav_path)

        ########## Transcribe ##########
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        logger.info("Transcribing...")
        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = whisper_model.transcribe('output.wav')
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        if response["success"]:
            logger.info("You said: %s", response["transcription"]["text"])
        else:
            logger.warning("Transcribe failed.")
            logger.warning("%s", response["error"])

    else:
        response = {"success": True, "error": None, "transcription": {"text": input("Enter your prompt: ")}}

    ########## LLM ##########
    if enable_LLM_module:
        user_response_to_prompt = {"role": "user", "content": ""}
        user_response_to_prompt["content"] = response["transcription"]["text"]
        llm_prompt.append(user_response_to_prompt)

        logger.info("Calling LLM API")
        llm_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=llm_prompt
        )
        # user_response_to_prompt["content"] = input(f"Assistant: {response.choices[0].message.content} \nYou:")
        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        llm_response_to_prompt = {"role": "system", "name": "Assistant",
                                  "content": llm_response.choices[0].message.content}
        llm_prompt.append(llm_response_to_prompt)

    ########## TTS ##########
    if enable_TTS_module:
        # Stream audio
        text_to_stream = llm_response.choices[0].message.content
        voice_id = "Liv"
        bitrate = "192k"
        speed = 0
        pitch = 1.1
        logger.info("Calling TTS API")

        # Generate audio from text
        tts_audio_data = speech_api.speech(text=text_to_stream, voice_id=voice_id, bitrate=bitrate, speed=speed,
                                           pitch=pitch)

        # Play audio
        logger.info("Playing TTS audio")
        play(tts_audio_data)
