from flask import Flask, request, jsonify
import requests, base64, xxtea, brotli
from Crypto.Cipher import AES
from google.protobuf import json_format
import player_info_pb2 as pb
from map_proto_pb2 import CraftlandMapList

app = Flask(__name__)

XXTEA_KEY = b'SKg83F53jdmfe5t0'
CRAFT_AES_KEY = b"YAkD*#o6C1Ls@VjR"
CRAFT_AES_IV = b"\0" * 16
JWT_URL = "https://starexxlab-jwt.vercel.app/token"

def encrypt_uid(uid):
    return base64.b64encode(xxtea.encrypt(uid.encode(), XXTEA_KEY)).decode()

def decrypt_response(data):
    return brotli.decompress(data)

def get_jwt():
    try:
        return requests.get(JWT_URL).text
    except:
        return None

def decrypt_craftland_response(data):
    cipher = AES.new(CRAFT_AES_KEY, AES.MODE_CBC, CRAFT_AES_IV)
    decrypted = cipher.decrypt(data)
    return decrypted.rstrip(b'\x00')

@app.route("/")
def home():
    return "Free Fire Player Info API is live!"

@app.route("/player-info/<region>/<uid>", methods=["GET"])
def player_info(region, uid):
    encrypted_uid = encrypt_uid(uid)
    jwt = get_jwt()
    if not jwt:
        return jsonify({"error": "JWT fetch failed"}), 500

    # Player Info
    url = f"https://{region}mob.coldgameapi.com/api/player/getotherprofile"
    headers = {
        "authorization": jwt,
        "User-Agent": "FreeFire/1.99.1",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    res = requests.post(url, data=f"target_uid={encrypted_uid}", headers=headers)
    if res.status_code != 200:
        return jsonify({"error": "Player info failed"}), 500

    pb_data = pb.PlayerProfile()
    pb_data.ParseFromString(decrypt_response(res.content))
    data = json_format.MessageToDict(pb_data, preserving_proto_field_name=True)

    # Craftland
    craft_url = "https://client.ind.freefiremobile.com/GetUserCraftlandMapList"
    aes = AES.new(CRAFT_AES_KEY, AES.MODE_CBC, CRAFT_AES_IV)
    pad_len = 16 - len(f"user_id={uid}") % 16
    payload = f"user_id={uid}" + chr(pad_len) * pad_len
    enc_payload = aes.encrypt(payload.encode())
    c_headers = {
        "User-Agent": "FreeFireAdvanced/1.99.1",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Client-Version": "1.99.1",
    }
    c_res = requests.post(craft_url, data=enc_payload, headers=c_headers)

    craft_maps = []
    if c_res.status_code == 200:
        maps_pb = CraftlandMapList()
        maps_pb.ParseFromString(decrypt_craftland_response(c_res.content))
        for m in maps_pb.maps:
            if m.HasField("public_id") and m.public_id:
                craft_maps.append({
                    "name": m.name,
                    "likes": m.likes,
                    "plays": m.plays,
                    "shares": m.shares,
                    "code": m.public_id
                })

    # Final JSON
    final = {
        "account_basic_info": {
            "name": data.get("basic_info", {}).get("nick", "Not Found"),
            "uid": data.get("basic_info", {}).get("user_id", "Not Found"),
            "level": data.get("basic_info", {}).get("level", 0),
            "exp": data.get("basic_info", {}).get("exp", 0),
            "region": region.upper(),
            "likes": data.get("basic_info", {}).get("like", 0),
            "honor_score": data.get("credit_score_info", {}).get("score", 0),
            "celebrity": data.get("basic_info", {}).get("is_streamer", False),
            "evo_badge": "Active" if data.get("basic_info", {}).get("is_display_evo_gun_badge") else "Inactive",
            "title": data.get("social_info", {}).get("title", "Not Found"),
            "signature": data.get("social_info", {}).get("signature", "Not Found")
        },
        "account_activity": {
            "most_recent_ob": data.get("basic_info", {}).get("client_version", "Not Found"),
            "fire_pass": data.get("profile_info", {}).get("pass_info", {}).get("type", "Unknown"),
            "bp_badges": data.get("profile_info", {}).get("pass_info", {}).get("current_badge", "Not Found"),
            "br_rank": data.get("profile_info", {}).get("br_rank_info", {}).get("rank_desc", "Not Found"),
            "br_points": data.get("profile_info", {}).get("br_rank_info", {}).get("score", "Not Found"),
            "cs_rank": data.get("profile_info", {}).get("cs_rank_info", {}).get("rank_desc", "Not Found"),
            "cs_points": data.get("profile_info", {}).get("cs_rank_info", {}).get("score", "Not Found"),
            "created_at": data.get("profile_info", {}).get("register_time", "Not Found"),
            "last_login": data.get("profile_info", {}).get("last_login_time", "Not Found")
        },
        "account_overview": {
            "avatar_id": data.get("profile_info", {}).get("avatar", "Not Found"),
            "banner_id": data.get("profile_info", {}).get("banner", "Not Found"),
            "pin_id": data.get("profile_info", {}).get("custom_pin", "Not Found"),
            "equipped_skills": [
                x.get("name", "Unknown") + " (P)" for x in data.get("profile_info", {}).get("selected_skills", [])
            ],
            "gun_id": data.get("profile_info", {}).get("selected_guns", [{}])[0].get("gun_id", "Not Found"),
            "animation_id": data.get("profile_info", {}).get("animation", "Not Found"),
            "transform_animation_id": data.get("profile_info", {}).get("transform", "Not Found"),
            "outfits": "Graphically Presented Below"
        },
        "pet_info": {
            "equipped": bool(data.get("pet_info")),
            "pet_name": data.get("pet_info", {}).get("name", "Not Found"),
            "pet_type": data.get("pet_info", {}).get("pet_id", "Not Found"),
            "pet_exp": data.get("pet_info", {}).get("exp", 0),
            "pet_level": data.get("pet_info", {}).get("level", 0)
        },
        "guild_info": {
            "name": data.get("clan_basic_info", {}).get("name", "Not Found"),
            "id": data.get("clan_basic_info", {}).get("clan_id", "Not Found"),
            "level": data.get("clan_basic_info", {}).get("level", 0),
            "members": data.get("clan_basic_info", {}).get("member_num", 0),
            "leader": {
                "name": data.get("captain_basic_info", {}).get("nick", "Not Found"),
                "uid": data.get("captain_basic_info", {}).get("user_id", "Not Found"),
                "level": data.get("captain_basic_info", {}).get("level", 0),
                "exp": data.get("captain_basic_info", {}).get("exp", 0),
                "created_at": data.get("captain_basic_info", {}).get("register_time", "Not Found"),
                "last_login": data.get("captain_basic_info", {}).get("last_login_time", "Not Found"),
                "title": data.get("captain_basic_info", {}).get("title", "Not Found"),
                "bp_badges": data.get("captain_basic_info", {}).get("pass_info", {}).get("current_badge", "Not Found"),
                "br_points": data.get("captain_basic_info", {}).get("br_rank_info", {}).get("score", "Not Found"),
                "cs_points": data.get("captain_basic_info", {}).get("cs_rank_info", {}).get("score", "Not Found")
            }
        },
        "craftland_maps": craft_maps if craft_maps else "Not Found"
    }

    return jsonify(final)

if __name__ == "__main__":
    app.run()
