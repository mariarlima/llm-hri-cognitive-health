config = {
    "is_using_voice": True,
    "is_playback": False,
    "language":
        {
            "default": "en",
            "P21": "es",
        },
    "whisper_model_id":  # "tiny.en", first try: "base.en", then: "small.en", "medium.en",
        {
            "default": "tiny.en",
            "P03": "base.en",
            "P04": "base.en",
            "P05": "base.en",
            "P07": "small.en",
            "P08": "base.en",
            "P10": "small.en",
            "P12": "base.en",
            "P13": "small.en",
        },
    "enable_LLM_module": True,
    "enable_TTS_module": True,
    "STT":
        {
            "free_speech":
                {
                    "pause_threshold":  # Only stop recording after X second of silence
                        {
                            "Picture_1": 7,
                            "Picture_2": 7,
                            "Semantic_1": 15,
                            "Semantic_2": 15,
                        },
                    "phrase_time_limit":  # Max duration of a recorded audio clip
                        {
                            "Picture_1": 85,
                            "Picture_2": 85,
                            "Semantic_1": 60,
                            "Semantic_2": 60,
                        },
                },
            "normal":
                {
                    "pause_threshold":  # Only stop recording after 5 second of silence
                        {
                            "default": 4,
                            "P04": 5,
                            "P06": 6,
                            "P07": 6,
                            "P12": 5,
                            "P13": 5,
                        },
                    "phrase_time_limit": 60,  # Max duration of a recorded audio clip
                },
            "open_dialog":
            {
                "pause_threshold": 2,
                "phrase_time_limit": 10,

            },
            "timeout": 10,  # How much time r.listen will wait before a speech is picked up by mic
            "mic_time_offset": -0.05,  # Time offset for mic to start recording, seconds
        },
    "llm_model_id": "gpt-4o",
    "TTS":
        {
            "api_provider": "unrealspeech",  # unrealspeech, openai, aws
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
                },
            "aws":
                {
                    "voice_id": "Penelope",
                }
        },
    "Blossom":
        {
            "status": "Disabled",  # Enabled or Disabled
            "use_network_controller": True,  # to use AWS instance server and Raspberry Pi
            "sequence_length_boundary_list": {"prompt": [2, 3, 4, 5, 6, 7, 8, 9, 12, 17, 20]},
            "sequence_list":
                {
                    "start": ["cognitive/intro_01", "cognitive/intro_02", "cognitive/intro_03"],
                    "prompt": ["cognitive/encouragement_01", "cognitive/encouragement_02", "cognitive/encouragement_03",
                               "cognitive/encouragement_04", "cognitive/encouragement_05",
                               "cognitive/encouragement_06"],
                    "prompt_timed":
                        [
                            ["happy/happy_1_109", "happy/happy_2_109", "happy/happy_5_109", "happy/happy_8_109",
                             "happy/happy_9_109"],
                            ["yes", "fear/fear_startled"],
                            ["happy/happy_nodding", "happy/happy", "anger/anger_dissapoint"],
                            ["grand/grand4", "sesame/sesame12", "fear/fear"],
                            ["cognitive/encouragement_04", "happy/happy_head_bobbing", "fear/fear_looking_around_1"],
                            ["cognitive/encouragement_01", "happy/happy_daydream"],
                            ["cognitive/encouragement_03", "cognitive/encouragement_05"],
                            ["cognitive/encouragement_06", "cognitive/encouragement_02", "happy/happy_20181204_122044",
                             "happy/happy_20181204_120338"],
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
                    "prompt":
                    {
                        "en": "llm_prompt_t1_v1",
                        "es": "llm_prompt_t1_v1_ES",
                    },
                    "start_watermark": "storytelling",
                    "end_watermark": "next challenge",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Picture_2":
                {
                    "free_speech_watermark": "storytelling",
                    "prompt": 
                    {
                        "en": "llm_prompt_t1_v2",
                        "es": "llm_prompt_t1_v2_ES",
                    },
                    "start_watermark": "storytelling",
                    "end_watermark": "next challenge",
                    "end_blossom": "Great job! You described the picture in great detail. You’re ready for the next challenge!"
                },
            "Semantic_1":
                {
                    "free_speech_watermark": "different game",
                    "prompt": 
                    {
                        "en": "llm_prompt_t2_v1",
                        "es": "llm_prompt_t2_v1_ES",
                    },
                    "start_watermark": "different game",
                    "end_watermark": "bye",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Bye"
                },
            "Semantic_2":
                {
                    "free_speech_watermark": "different game",
                    "prompt": 
                    {
                        "en": "llm_prompt_t2_v2",
                        "es": "llm_prompt_t2_v2_ES",
                    },
                    "start_watermark": "different game",
                    "end_watermark": "bye",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Goodbye"
                },
            "Open_dialog":
            {
                 "free_speech_watermark": "different game",
                    "prompt": 
                    {
                        "en": "llm_prompt_open",
                        "es": "llm_prompt_open_ES",
                    },
                    "start_watermark": "different game",
                    "end_watermark": "bye",
                    "end_blossom": "Thank you for playing this game with me! It was so much fun! Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! Goodbye"
                },
                
            }
        }
