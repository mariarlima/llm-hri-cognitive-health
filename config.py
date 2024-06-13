config = {
    "is_using_voice": True,
    "is_playback": False,
    "whisper_model_id": "tiny.en",  # "tiny.en", first try: "base.en", then: "small.en", 
    "enable_LLM_module": True,
    "enable_TTS_module": True,
    "STT":
        {
            "free_speech":
                {
                    "pause_threshold": 6,  # Only stop recording after 5 second of silence
                    "phrase_time_limit": 80,  # Max duration of a recorded audio clip
                },
            "normal":
                {
                    "pause_threshold": 3,  # Only stop recording after 5 second of silence
                    "pause_threshold_task_1": 3,
                    "phrase_time_limit": 60,  # Max duration of a recorded audio clip
                },
            "timeout": 10,  # How much time r.listen will wait before a speech is picked up by mic
            "mic_time_offset": -0.05,  # Time offset for mic to start recording, seconds
        },
    "llm_model_id": "gpt-4o",  # "gpt-4-turbo",
    "TTS":
        {
            "api_provider": "unrealspeech",  # unrealspeech or openai
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
            "use_network_controller": False, # to use AWS instance server and Raspberry Pi 
            "sequence_length_boundary_list": {"prompt": [2, 3, 4, 5, 6, 7, 8, 9, 12, 17, 20]},
            "sequence_list":
                {
                    "start": ["cognitive/intro_01", "cognitive/intro_02", "cognitive/intro_03"],
                    "prompt": ["cognitive/encouragement_01", "cognitive/encouragement_02", "cognitive/encouragement_03",
                               "cognitive/encouragement_04", "cognitive/encouragement_05",
                               "cognitive/encouragement_06"],
                    "prompt_timed":
                        [
                            ["happy/happy_1_109", "happy/happy_2_109", "happy/happy_5_109", "happy/happy_8_109", "happy/happy_9_109" ],
                            ["yes", "fear/fear_startled"],
                            ["happy/happy_nodding", "happy/happy", "anger/anger_dissapoint"],
                            ["grand/grand4", "sesame/sesame12", "fear/fear"],
                            ["cognitive/encouragement_04", "happy/happy_head_bobbing", "fear/fear_looking_around_1"],
                            ["cognitive/encouragement_01", "happy/happy_daydream"],
                            ["cognitive/encouragement_03", "cognitive/encouragement_05"],
                            ["cognitive/encouragement_06", "cognitive/encouragement_02", "happy/happy_20181204_122044", "happy/happy_20181204_120338"],
                            ["cognitive/end_01", "cognitive/end_02"],
                            ["cognitive/end_03", "cognitive/intro_03"],
                            ["cognitive/intro_01", "cognitive/intro_02"]
                        ],
                    "end": ["cognitive/end_01", "cognitive/end_02", "cognitive/end_03"],
                },
            "delay": 0.8,
            "delay_intro": 0.75,
        },
    "Task":
        {
            "Picture_1":
                {
                    "free_speech_watermark": "storytelling",
                    "prompt": "llm_prompt_task1_1",
                    "start_watermark": "storytelling",
                    "end_watermark": "next challenge",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Picture_2":
                {
                    "free_speech_watermark": "storytelling",
                    "prompt": "llm_prompt_task1_2",
                    "start_watermark": "storytelling",
                    "end_watermark": "next challenge",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Semantic_1":
                {
                    "free_speech_watermark": "different game",
                    "prompt": "llm_prompt_task2_1",
                    "start_watermark": "different game",
                    "end_watermark": "bye",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Bye"
                },
            "Semantic_2":
                {
                    "free_speech_watermark": "different game",
                    "prompt": "llm_prompt_task2_2",
                    "start_watermark": "different game",
                    "end_watermark": "bye",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Goodbye"
                }
        },
}
