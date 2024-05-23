config = {
    "is_using_voice": True,
    "is_playback": False,
    "whisper_model_id": "tiny.en",  # "medium.en",
    "enable_LLM_module": True,
    "enable_TTS_module": True,
    "STT":
        {
            "free_speech":
                {
                    "pause_threshold": 7,  # Only stop recording after 5 second of silence
                    "phrase_time_limit": 60,  # Max duration of a recorded audio clip
                },
            "normal":
                {
                    "pause_threshold": 7,  # Only stop recording after 5 second of silence
                    "phrase_time_limit": 0,  # Max duration of a recorded audio clip
                },
            "timeout": 10,  # How much time r.listen will wait before a speech is picked up by mic
            "mic_time_offset": 0.0,  # Time offset for mic to start recording
        },
    "llm_model_id": "gpt-4o",  # "gpt-4-turbo",
    "TTS":
        {
            "api_provider": "openai",  # unrealspeech or openai
            "unrealspeech":
                {
                    "voice_id": "Amy",
                    "bit_rate": "192k",
                    "speed": -0.25,
                    "pitch": 1.09,
                },
            "openai":
                {
                    "model_id": "tts-1",
                    "voice_id": "alloy"
                }
        },
    "Blossom":
        {
            "status": "Enabled",  # Enabled or Disabled
            "sequence_list":
                {
                    "start": ["cognitive/intro_01", "cognitive/intro_02", "cognitive/intro_03"],
                    "prompt": ["cognitive/encouragement_01", "cognitive/encouragement_02", "cognitive/encouragement_03",
                               "cognitive/encouragement_04", "cognitive/encouragement_05",
                               "cognitive/encouragement_06"],
                    "end": ["cognitive/end_01", "cognitive/end_02", "cognitive/end_03"],
                },
            "delay": 0.8,
            "delay_intro": 0.8,
        },
    "Task":
        {
            "Picture_1":
                {
                    "free_speech_watermark": "storytelling",
                    "prompt": "llm_prompt_task1_1",
                    "start_watermark": "storytelling",
                    "end_watermark": "bye",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Picture_2":
                {
                    "free_speech_watermark": "storytelling",
                    "prompt": "llm_prompt_task1_2",
                    "start_watermark": "storytelling",
                    "end_watermark": "bye",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Semantic_1":
                {
                    "free_speech_watermark": "different game",
                    "prompt": "llm_prompt_task2_1",
                    "start_watermark": "different game",
                    "end_watermark": "next challenge",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Bye"
                },
            "Semantic_2":
                {
                    "free_speech_watermark": "different game",
                    "prompt": "llm_prompt_task2_2",
                    "start_watermark": "different game",
                    "end_watermark": "next challenge",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Goodbye"
                }
        },
}
