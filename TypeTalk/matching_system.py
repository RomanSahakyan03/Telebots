import os
import json
import time
import random
from config import create_redis_client
from db import BotDB
from utils import haversine_distance, from_coords_to_name, mbti_types, sexes, system_delete_message, system_send_message, make_pair


# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute texts path
texts_path = os.path.join(current_dir, 'typetalk_texts.json')

# Construct the absolute texts path
db_path = os.path.join(current_dir, 'userdata.db')

db = BotDB(db_path)
cache = create_redis_client()

with open(texts_path, 'r', encoding="UTF-8") as f:
    texts = json.load(f)


def matching_system():
    while True:
        while cache.scard("waiting_pool") < 2:
            time.sleep(2) # adjustable
        print("the elems are more than two")
        chat_id1, chat_id2 = cache.srandmember("waiting_pool", 2)
        chat_id1 = int(chat_id1)
        chat_id2 = int(chat_id2)
        params1 = db.select_parameter("*", f"chat_id = {chat_id1}")
        params2 = db.select_parameter("*", f"chat_id = {chat_id2}")

        first_type = params1["TYPE"]
        first_types = params1["TYPES"]
        second_type = params2["TYPE"]
        second_types = params2["TYPES"]


        # if no one selected <=> all types available
        if int(first_types) == 0:
            first_types = 65535 
        if int(second_types) == 0:
            second_types = 65535


        is_type1 = bool(int(second_types) & (1 << int(first_type)))
        is_type2 = bool(int(first_types) & (1 << int(second_type)))

        if not is_type1 or not is_type2:
            continue
        print("types matching passed")

        first_age = params1["age"]
        first_ages = params1["preferred_ages"]
        second_age = params2["age"]
        second_ages = params2["preferred_ages"]
        second_ages = second_ages.split('-')

        if not (int(second_ages[0]) <= int(first_age) <= int(second_ages[1])):
            continue

        first_ages = first_ages.split('-')

        if not (int(first_ages[0]) <= int(second_age) <= int(first_ages[1])):
            continue

        print("age matching passed")
        first_lat = params1["region_lat"]
        first_lon = params1["region_lon"]
        second_lat = params2["region_lat"]
        second_lon = params2["region_lon"]


        if bool(first_lat) ^ bool(second_lat):
            continue
        else:
            if first_lat and haversine_distance(first_lat, first_lon, second_lat, second_lon) > 67.4:
                continue
            else:
                if lang1 != lang2:
                    if random.random() > 0.4:
                        continue
                        
        print("region match ing passed")

        sex1 = params1["sex"]
        sex2 = params1["sex"]
        sexes1 = params1["sexes"]
        sexes2 = params1["sexes"]

        if sexes1 != 2 and ((sex1 ^ 1) != sexes2):
            continue

        if sexes2 != 2 and ((sex2 ^ 1) != sexes1):
            continue

        lang1 = params1["language"]
        lang2 = params2["language"]

        text1 = f"{texts['matching']['partner found'][lang1]}\n"
        text1 += f"{texts['matching']['age'][lang1]}{second_age}\n"
        if first_lat:
            text1 += f"{texts['matching']['region'][lang1]}{from_coords_to_name(second_lat, second_lon, lang1)}\n"
        text1 += f"{texts['matching']['type'][lang1]}{mbti_types[second_type]}\n"
        text1 += f"{texts['matching']['sex'][lang1]}{texts[sexes[sex2]][lang1]}"

        text2 = f"{texts['matching']['partner found'][lang2]}\n"
        text2 += f"{texts['matching']['age'][lang2]}{first_age}\n"
        if second_lat:
             text2 += f"{texts['matching']['region'][lang2]}{from_coords_to_name(first_lat, first_lon, lang2)}\n"
        text2 += f"{texts['matching']['type'][lang2]}{mbti_types[first_type]}\n"
        text2 += f"{texts['matching']['sex'][lang2]}{texts[sexes[sex1]][lang2]}"

        system_delete_message(chat_id1, int(cache.hget("waiting_message", chat_id1)))
        system_delete_message(chat_id2, int(cache.hget("waiting_message", chat_id2)))
        cache.srem("waiting_pool", chat_id1, chat_id2)
        cache.hdel("waiting_message", chat_id1, chat_id2)
        system_send_message(chat_id1, text1, {"remove_keyboard" : True}, "partner message")
        system_send_message(chat_id2, text2, {"remove_keyboard" : True}, "partner message")

        make_pair(chat_id1, chat_id2)


        print("end matching ")