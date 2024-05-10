config = {
    "is_using_voice": True,
    "is_playback": False,
    "whisper_model_id": "medium.en",
    "enable_LLM_module": True,
    "enable_TTS_module": True,
    # "wav_path": 'output.wav',
    "STT":
        {
            "pause_threshold": 5,  # Only stop recording after 5 second of silence
            "timeout": 10,  # How much time r.listen will wait before a speech is picked up by mic
            "phrase_time_limit": 20,  # Max duration of a recorded audio clip
        },
    "llm_model_id": "gpt-3.5-turbo",
    "TTS":
        {
            "api_provider": "unrealspeech",  # unrealspeech or openai
            "unrealspeech":
                {
                    "voice_id": "Liv",
                    "bit_rate": "192k",
                    "speed": 0,
                    "pitch": 1.1
                },
            "openai":
                {
                    "model_id": "tts-1",
                    "voice_id": "alloy"
                }
        },
}
