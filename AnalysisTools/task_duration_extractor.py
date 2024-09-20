import re
from datetime import timedelta


def parse_time(time_str):
    """Parse time string in the format 'MM:SS' and return a timedelta object."""
    minutes, seconds = map(int, time_str.split(':'))
    return timedelta(minutes=minutes, seconds=seconds)


def calculate_duration(start_time, end_time):
    """Calculate the duration between two timestamps."""
    return end_time - start_time


def extract_info_and_calculate_duration(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Extract the "Pxx Sx" part
        match = re.search(r'P\d{2}_S\d', line)
        if not match:
            continue

        video_name = match.group(0).replace('_', ' ')  # Format it as "Pxx Sx"

        # Extract the timestamps
        timestamps = re.findall(r'\((\d{2}:\d{2}),(\d{2}:\d{2})\)', line)

        if len(timestamps) == 2:
            start1, end1 = timestamps[0]
            start2, end2 = timestamps[1]

            # Calculate durations
            duration1 = calculate_duration(parse_time(start1), parse_time(end1))
            duration2 = calculate_duration(parse_time(start2), parse_time(end2))
            total_duration = duration1 + duration2

            # Convert timedelta to minutes and seconds
            duration1_seconds = int(duration1.total_seconds())
            duration2_seconds = int(duration2.total_seconds())
            total_seconds = int(total_duration.total_seconds())

            print(
                f"{video_name}: Duration1 = {duration1_seconds} seconds, Duration2 = {duration2_seconds} seconds, Total Duration = {total_seconds} seconds")


file_path = 'video_slicing.sh'
extract_info_and_calculate_duration(file_path)

# import re
# from datetime import timedelta
#
#
# def parse_time(time_str):
#     """Parse time string in the format 'MM:SS' and return a timedelta object."""
#     minutes, seconds = map(int, time_str.split(':'))
#     return timedelta(minutes=minutes, seconds=seconds)
#
#
# def calculate_duration(start_time, end_time):
#     """Calculate the duration between two timestamps."""
#     return end_time - start_time
#
#
# def extract_info_and_calculate_duration(file_path):
#     video_durations = []
#
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#
#     for line in lines:
#         # Extract the "Pxx Sx" part
#         match = re.search(r'P\d{2}_S\d', line)
#         if not match:
#             continue
#
#         video_name = match.group(0).replace('_', ' ')  # Format it as "Pxx Sx"
#
#         # Extract the timestamps
#         timestamps = re.findall(r'\((\d{2}:\d{2}),(\d{2}:\d{2})\)', line)
#
#         if len(timestamps) == 2:
#             start1, end1 = timestamps[0]
#             start2, end2 = timestamps[1]
#
#             # Calculate durations
#             duration1 = calculate_duration(parse_time(start1), parse_time(end1))
#             duration2 = calculate_duration(parse_time(start2), parse_time(end2))
#             total_duration = duration1 + duration2
#
#             # Convert timedelta to seconds
#             duration1_seconds = int(duration1.total_seconds())
#             duration2_seconds = int(duration2.total_seconds())
#             total_seconds = int(total_duration.total_seconds())
#
#             # Append to list for sorting later
#             video_durations.append((video_name, duration1_seconds, duration2_seconds, total_seconds))
#
#     return video_durations
#
#
# def sort_video_durations(video_durations):
#     """Sort the list of video durations by 'Pxx Sx'."""
#     return sorted(video_durations, key=lambda x: x[0])
#
#
# def display_sorted_durations(file_path):
#     # Extract and calculate durations
#     video_durations = extract_info_and_calculate_duration(file_path)
#
#     # Sort by video_name (Pxx Sx)
#     sorted_videos = sort_video_durations(video_durations)
#
#     # Print sorted results
#     for video_name, duration1, duration2, total_duration in sorted_videos:
#         print(
#             f"{video_name}: Duration1 = {duration1} seconds, Duration2 = {duration2} seconds, Total Duration = {total_duration} seconds")
#
#
# # Usage example
# file_path = 'video_slicing.sh'  # Replace with your txt file path
# display_sorted_durations(file_path)

# P01 S1: Duration1 = 265 seconds, Duration2 = 249 seconds, Total Duration = 514 seconds
# P01 S2: Duration1 = 247 seconds, Duration2 = 267 seconds, Total Duration = 514 seconds
# P02 S1: Duration1 = 291 seconds, Duration2 = 238 seconds, Total Duration = 529 seconds
# P02 S2: Duration1 = 270 seconds, Duration2 = 261 seconds, Total Duration = 531 seconds
# P02 S3: Duration1 = 322 seconds, Duration2 = 311 seconds, Total Duration = 633 seconds
# P02 S4: Duration1 = 338 seconds, Duration2 = 364 seconds, Total Duration = 702 seconds
# P02 S5: Duration1 = 286 seconds, Duration2 = 193 seconds, Total Duration = 479 seconds
# P03 S1: Duration1 = 224 seconds, Duration2 = 227 seconds, Total Duration = 451 seconds
# P03 S2: Duration1 = 486 seconds, Duration2 = 274 seconds, Total Duration = 760 seconds
# P04 S1: Duration1 = 210 seconds, Duration2 = 206 seconds, Total Duration = 416 seconds
# P04 S2: Duration1 = 310 seconds, Duration2 = 281 seconds, Total Duration = 591 seconds
# P04 S3: Duration1 = 321 seconds, Duration2 = 335 seconds, Total Duration = 656 seconds
# P04 S4: Duration1 = 303 seconds, Duration2 = 354 seconds, Total Duration = 657 seconds
# P04 S5: Duration1 = 279 seconds, Duration2 = 233 seconds, Total Duration = 512 seconds
# P05 S1: Duration1 = 250 seconds, Duration2 = 257 seconds, Total Duration = 507 seconds
# P05 S2: Duration1 = 246 seconds, Duration2 = 277 seconds, Total Duration = 523 seconds
# P05 S3: Duration1 = 366 seconds, Duration2 = 334 seconds, Total Duration = 700 seconds
# P05 S4: Duration1 = 258 seconds, Duration2 = 344 seconds, Total Duration = 602 seconds
# P05 S5: Duration1 = 249 seconds, Duration2 = 244 seconds, Total Duration = 493 seconds
# P06 S1: Duration1 = 176 seconds, Duration2 = 285 seconds, Total Duration = 461 seconds
# P06 S2: Duration1 = 314 seconds, Duration2 = 320 seconds, Total Duration = 634 seconds
# P06 S3: Duration1 = 345 seconds, Duration2 = 335 seconds, Total Duration = 680 seconds
# P06 S4: Duration1 = 176 seconds, Duration2 = 317 seconds, Total Duration = 493 seconds
# P06 S5: Duration1 = 154 seconds, Duration2 = 211 seconds, Total Duration = 365 seconds
# P07 S1: Duration1 = 203 seconds, Duration2 = 224 seconds, Total Duration = 427 seconds
# P07 S2: Duration1 = 353 seconds, Duration2 = 326 seconds, Total Duration = 679 seconds
# P07 S3: Duration1 = 342 seconds, Duration2 = 337 seconds, Total Duration = 679 seconds
# P07 S4: Duration1 = 324 seconds, Duration2 = 348 seconds, Total Duration = 672 seconds
# P07 S5: Duration1 = 204 seconds, Duration2 = 281 seconds, Total Duration = 485 seconds
# P08 S1: Duration1 = 175 seconds, Duration2 = 230 seconds, Total Duration = 405 seconds
# P08 S2: Duration1 = 326 seconds, Duration2 = 317 seconds, Total Duration = 643 seconds
# P08 S3: Duration1 = 225 seconds, Duration2 = 348 seconds, Total Duration = 573 seconds
# P08 S4: Duration1 = 336 seconds, Duration2 = 338 seconds, Total Duration = 674 seconds
# P08 S5: Duration1 = 191 seconds, Duration2 = 267 seconds, Total Duration = 458 seconds
# P09 S1: Duration1 = 204 seconds, Duration2 = 250 seconds, Total Duration = 454 seconds
# P09 S2: Duration1 = 325 seconds, Duration2 = 264 seconds, Total Duration = 589 seconds
# P09 S3: Duration1 = 250 seconds, Duration2 = 292 seconds, Total Duration = 542 seconds
# P09 S4: Duration1 = 322 seconds, Duration2 = 334 seconds, Total Duration = 656 seconds
# P09 S5: Duration1 = 201 seconds, Duration2 = 217 seconds, Total Duration = 418 seconds
# P10 S1: Duration1 = 191 seconds, Duration2 = 282 seconds, Total Duration = 473 seconds
# P10 S2: Duration1 = 261 seconds, Duration2 = 276 seconds, Total Duration = 537 seconds
# P10 S3: Duration1 = 363 seconds, Duration2 = 306 seconds, Total Duration = 669 seconds
# P10 S4: Duration1 = 170 seconds, Duration2 = 299 seconds, Total Duration = 469 seconds
# P10 S5: Duration1 = 149 seconds, Duration2 = 179 seconds, Total Duration = 328 seconds
# P11 S1: Duration1 = 181 seconds, Duration2 = 311 seconds, Total Duration = 492 seconds
# P11 S2: Duration1 = 320 seconds, Duration2 = 311 seconds, Total Duration = 631 seconds
# P12 S1: Duration1 = 201 seconds, Duration2 = 245 seconds, Total Duration = 446 seconds
# P12 S2: Duration1 = 371 seconds, Duration2 = 272 seconds, Total Duration = 643 seconds
# P12 S3: Duration1 = 311 seconds, Duration2 = 320 seconds, Total Duration = 631 seconds
# P12 S4: Duration1 = 280 seconds, Duration2 = 338 seconds, Total Duration = 618 seconds
# P12 S5: Duration1 = 167 seconds, Duration2 = 201 seconds, Total Duration = 368 seconds
# P13 S1: Duration1 = 295 seconds, Duration2 = 448 seconds, Total Duration = 743 seconds
# P13 S2: Duration1 = 334 seconds, Duration2 = 322 seconds, Total Duration = 656 seconds
# P13 S3: Duration1 = 308 seconds, Duration2 = 326 seconds, Total Duration = 634 seconds
# P13 S4: Duration1 = 336 seconds, Duration2 = 273 seconds, Total Duration = 609 seconds
# P13 S5: Duration1 = 335 seconds, Duration2 = 346 seconds, Total Duration = 681 seconds
# P14 S1: Duration1 = 150 seconds, Duration2 = 210 seconds, Total Duration = 360 seconds
# P14 S2: Duration1 = 242 seconds, Duration2 = 315 seconds, Total Duration = 557 seconds
# P14 S3: Duration1 = 246 seconds, Duration2 = 333 seconds, Total Duration = 579 seconds
# P14 S4: Duration1 = 250 seconds, Duration2 = 269 seconds, Total Duration = 519 seconds
# P14 S5: Duration1 = 163 seconds, Duration2 = 259 seconds, Total Duration = 422 seconds
# P15 S1: Duration1 = 161 seconds, Duration2 = 257 seconds, Total Duration = 418 seconds
# P15 S2: Duration1 = 323 seconds, Duration2 = 318 seconds, Total Duration = 641 seconds
# P15 S4: Duration1 = 335 seconds, Duration2 = 335 seconds, Total Duration = 670 seconds
# P15 S5: Duration1 = 140 seconds, Duration2 = 180 seconds, Total Duration = 320 seconds
# P16 S1: Duration1 = 263 seconds, Duration2 = 331 seconds, Total Duration = 594 seconds
# P16 S2: Duration1 = 326 seconds, Duration2 = 336 seconds, Total Duration = 662 seconds
# P16 S3: Duration1 = 362 seconds, Duration2 = 346 seconds, Total Duration = 708 seconds
# P16 S4: Duration1 = 391 seconds, Duration2 = 361 seconds, Total Duration = 752 seconds
# P16 S5: Duration1 = 223 seconds, Duration2 = 251 seconds, Total Duration = 474 seconds
# P17 S1: Duration1 = 312 seconds, Duration2 = 263 seconds, Total Duration = 575 seconds
# P17 S1: Duration1 = 250 seconds, Duration2 = 260 seconds, Total Duration = 510 seconds
# P17 S2: Duration1 = 283 seconds, Duration2 = 364 seconds, Total Duration = 647 seconds
# P17 S3: Duration1 = 324 seconds, Duration2 = 295 seconds, Total Duration = 619 seconds
# P17 S4: Duration1 = 204 seconds, Duration2 = 317 seconds, Total Duration = 521 seconds
# P17 S5: Duration1 = 240 seconds, Duration2 = 202 seconds, Total Duration = 442 seconds
# P18 S1: Duration1 = 214 seconds, Duration2 = 309 seconds, Total Duration = 523 seconds
# P18 S2: Duration1 = 330 seconds, Duration2 = 347 seconds, Total Duration = 677 seconds
# P18 S3: Duration1 = 258 seconds, Duration2 = 367 seconds, Total Duration = 625 seconds
# P18 S4: Duration1 = 345 seconds, Duration2 = 346 seconds, Total Duration = 691 seconds
# P18 S5: Duration1 = 232 seconds, Duration2 = 269 seconds, Total Duration = 501 seconds
# P19 S1: Duration1 = 258 seconds, Duration2 = 273 seconds, Total Duration = 531 seconds
# P19 S1: Duration1 = 190 seconds, Duration2 = 379 seconds, Total Duration = 569 seconds
# P19 S2: Duration1 = 235 seconds, Duration2 = 346 seconds, Total Duration = 581 seconds
# P19 S3: Duration1 = 294 seconds, Duration2 = 303 seconds, Total Duration = 597 seconds
# P19 S4: Duration1 = 312 seconds, Duration2 = 305 seconds, Total Duration = 617 seconds
# P19 S5: Duration1 = 284 seconds, Duration2 = 205 seconds, Total Duration = 489 seconds
# P20 S1: Duration1 = 199 seconds, Duration2 = 334 seconds, Total Duration = 533 seconds
# P20 S2: Duration1 = 235 seconds, Duration2 = 354 seconds, Total Duration = 589 seconds
# P20 S3: Duration1 = 206 seconds, Duration2 = 134 seconds, Total Duration = 340 seconds
# P20 S4: Duration1 = 278 seconds, Duration2 = 336 seconds, Total Duration = 614 seconds
# P20 S5: Duration1 = 197 seconds, Duration2 = 207 seconds, Total Duration = 404 seconds
# P21 S1: Duration1 = 190 seconds, Duration2 = 261 seconds, Total Duration = 451 seconds
# P21 S2: Duration1 = 327 seconds, Duration2 = 274 seconds, Total Duration = 601 seconds
# P21 S3: Duration1 = 171 seconds, Duration2 = 229 seconds, Total Duration = 400 seconds
# P21 S4: Duration1 = 300 seconds, Duration2 = 298 seconds, Total Duration = 598 seconds
# P21 S5: Duration1 = 180 seconds, Duration2 = 128 seconds, Total Duration = 308 seconds
# P22 S1: Duration1 = 285 seconds, Duration2 = 369 seconds, Total Duration = 654 seconds
# P22 S2: Duration1 = 320 seconds, Duration2 = 342 seconds, Total Duration = 662 seconds
# P22 S3: Duration1 = 271 seconds, Duration2 = 328 seconds, Total Duration = 599 seconds
# P22 S4: Duration1 = 257 seconds, Duration2 = 352 seconds, Total Duration = 609 seconds
# P22 S5: Duration1 = 277 seconds, Duration2 = 306 seconds, Total Duration = 583 seconds
# P23 S1: Duration1 = 178 seconds, Duration2 = 238 seconds, Total Duration = 416 seconds
# P23 S2: Duration1 = 330 seconds, Duration2 = 268 seconds, Total Duration = 598 seconds
# P23 S3: Duration1 = 363 seconds, Duration2 = 278 seconds, Total Duration = 641 seconds
# P23 S4: Duration1 = 326 seconds, Duration2 = 257 seconds, Total Duration = 583 seconds
# P23 S5: Duration1 = 309 seconds, Duration2 = 174 seconds, Total Duration = 483 seconds
# P24 S1: Duration1 = 197 seconds, Duration2 = 265 seconds, Total Duration = 462 seconds
# P24 S2: Duration1 = 260 seconds, Duration2 = 272 seconds, Total Duration = 532 seconds
# P24 S3: Duration1 = 306 seconds, Duration2 = 263 seconds, Total Duration = 569 seconds
# P24 S4: Duration1 = 312 seconds, Duration2 = 355 seconds, Total Duration = 667 seconds
# P24 S4: Duration1 = 312 seconds, Duration2 = 355 seconds, Total Duration = 667 seconds
# P24 S5: Duration1 = 222 seconds, Duration2 = 292 seconds, Total Duration = 514 seconds
# P25 S1: Duration1 = 170 seconds, Duration2 = 236 seconds, Total Duration = 406 seconds
# P25 S2: Duration1 = 291 seconds, Duration2 = 289 seconds, Total Duration = 580 seconds
# P25 S3: Duration1 = 270 seconds, Duration2 = 297 seconds, Total Duration = 567 seconds
# P25 S4: Duration1 = 241 seconds, Duration2 = 301 seconds, Total Duration = 542 seconds
# P25 S5: Duration1 = 137 seconds, Duration2 = 206 seconds, Total Duration = 343 seconds
#
# Process finished with exit code 0
