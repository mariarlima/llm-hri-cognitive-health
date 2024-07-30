#!/usr/bin/env python
# coding: utf-8

# ## Word Embedding


import os
import numpy as np
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def pad_embeddings(a, b):
    target_length = max(len(a), len(b))
    a = np.pad(a, (0, target_length - len(a)), 'constant')
    b = np.pad(b, (0, target_length - len(b)), 'constant')
    return a, b


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


baseline_cookie_text = """
In the picture, a busy scene in a kitchen is depicted. Here are the details:

1. **People**:
   - There is a woman, likely the mother, standing by the sink washing dishes. She is holding a plate and a dish towel.
   - A young boy is standing on a stool, reaching into an upper cabinet where there is a jar labeled "COOKIE JAR." He has one hand in the jar and appears to be retrieving a cookie.
   - A young girl stands next to the boy, reaching up as if to help or receive a cookie from him.

2. **Actions**:
   - The woman is washing dishes, but the sink is overflowing with water, which is spilling onto the floor.
   - The boy is taking cookies from the jar.
   - The girl is either reaching to help the boy or to receive a cookie from him.

3. **Objects**:
   - **Cookie jar**: Clearly labeled and located in an upper cabinet.
   - **Stool**: The boy is standing on it to reach the cookie jar.
   - **Sink**: Overflowing with water, indicating a possible plumbing issue or neglect due to distraction.
   - **Dishes**: The woman is holding one, and there are a few other dishes visible on the counter.

4. **Environment**:
   - **Kitchen**: The setting is a typical kitchen with cabinets, a counter, a sink, and a window.
   - **Window**: Through the window, a scene of a tree or bush is visible, suggesting it might be a backyard or garden view.
   - **Curtains**: The window has curtains that are pulled back.

The overall scene shows a mix of normal daily activity (dishwashing) with a bit of mischief (children reaching for cookies) and a potential mishap (overflowing sink).
"""

baseline_picnic_text = """
The picture depicts a lively and idyllic scene at a lakeside park where a family is enjoying a sunny day. Here's a detailed description of the various elements and activities happening in the scene:

1. **Foreground (Picnic Area)**:
    - A man is sitting on a picnic blanket, engrossed in a book. He wears glasses and casual summer attire.
    - A woman beside him is pouring a drink from a thermos into a cup, preparing for a picnic. There is a picnic basket and a portable radio on the blanket.
    - Nearby, a boy is running with a kite, enjoying the breeze. He is smiling and looks excited.
    - A dog is also part of the family fun, running joyfully with the boy.

2. **Middle Ground (Lakeside Activities)**:
    - A dock extends into the lake, where a person is fishing. They are standing at the edge of the dock, casting a line into the water.
    - A child is building a sandcastle at the edge of the lake, focused and using a bucket and a small shovel.

3. **Background (Scenic View)**:
    - There is a house with a car parked in the driveway, suggesting this is a residential area near the lake.
    - A tree with a full canopy of leaves is near the house, adding to the tranquil setting.
    - In the distance, a sailboat is gliding on the lake, adding to the sense of a perfect summer day.

The overall mood of the picture is joyful and relaxed, capturing the essence of a family enjoying quality time together in nature.
"""


def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return full_text


def read_and_compute(file_path, baseline):
    full_text_list = read_docx(file_path)

    t1_start_index = 0
    t1_end_index = 0
    for paragraph in full_text_list:
        if "storytelling" in paragraph.lower():
            break
        t1_start_index += 1
    for paragraph in full_text_list:
        if "t2" in paragraph.lower():
            break
        t1_end_index += 1

    # t2_start_index = 0
    # t2_end_index = len(full_text_list) - 1
    # for paragraph in full_text_list:
    #     if "different game" in paragraph.lower():
    #         break
    #     t2_start_index += 1

    t1 = (full_text_list[t1_start_index:t1_end_index])

    t1_processed = list(
        filter(lambda x: not ((x == "") or ("speaker 0" in x.lower()) or (x is None) or ("first prompt" in x.lower())),
               t1))

    for i in range(0, len(t1_processed)):
        t1_processed[i] = t1_processed[i].replace("Speaker 1: ", "")

    test_text = "".join(t1_processed)

    baseline_text_emb = get_embedding(baseline)
    test_text_emb = get_embedding(test_text)

    baseline_text_emb, test_text_emb = pad_embeddings(baseline_text_emb, test_text_emb)

    return cosine_similarity(baseline_text_emb, test_text_emb)

#
# print(f"P02 Cookie Theft Task: ")
# print(f"P02 S1: {read_and_compute('./data/P02_S1_check.docx', baseline_cookie_text)}")
# print(f"P02 S3: {read_and_compute('./data/P02_S3_check.docx', baseline_cookie_text)}")
# print(f"P02 S5: {read_and_compute('./data/P02_S5_check.docx', baseline_cookie_text)}")
# print(f"P02 Picnic Task: ")
# print(f"P02 S2: {read_and_compute('./data/P02_S2_check.docx', baseline_picnic_text)}")
# print(f"P02 S4: {read_and_compute('./data/P02_S4_check.docx', baseline_picnic_text)}")
#
# print(f"===============================================")
#
# print(f"P07 Cookie Theft Task: ")
# print(f"P07 S1: {read_and_compute('./data/P07_S1_check.docx', baseline_cookie_text)}")
# print(f"P07 S3: {read_and_compute('./data/P07_S3_check.docx', baseline_cookie_text)}")
# print(f"P07 S5: {read_and_compute('./data/P07_S5_check.docx', baseline_cookie_text)}")
# print(f"P07 Picnic Task: ")
# print(f"P07 S2: {read_and_compute('./data/P07_S2_check.docx', baseline_picnic_text)}")
# print(f"P07 S4: {read_and_compute('./data/P07_S4_check.docx', baseline_picnic_text)}")
#
# print(f"===============================================")
#
# print(f"P05 Cookie Theft Task: ")
# print(f"P05 S1: {read_and_compute('./data/P05_S1_check.docx', baseline_cookie_text)}")
# print(f"P05 S3: {read_and_compute('./data/P05_S3_check.docx', baseline_cookie_text)}")
# print(f"P05 S5: {read_and_compute('./data/P05_S5_check.docx', baseline_cookie_text)}")
# print(f"P05 Picnic Task: ")
# print(f"P05 S2: {read_and_compute('./data/P05_S2_check.docx', baseline_picnic_text)}")
# print(f"P05 S4: {read_and_compute('./data/P05_S4_check.docx', baseline_picnic_text)}")

# P02 Cookie Theft Task:
# P02 S1: 0.6939642079326661
# P02 S3: 0.7478055468023939
# P02 S5: 0.7240586258910455
# P02 Picnic Task:
# P02 S2: 0.5974089850474277
# P02 S4: 0.5869567996005751
# ===============================================
# P07 Cookie Theft Task:
# P07 S1: 0.44760570318832604
# P07 S3: 0.5741515796895419
# P07 S5: 0.6299557761963929
# P07 Picnic Task:
# P07 S2: 0.4864122731071448
# P07 S4: 0.5481734649878743
