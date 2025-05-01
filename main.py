from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

@app.route('/player-info/<region>/<uid>', methods=['GET'])
def get_player_info(region, uid):
    return jsonify({
        "account_info": {
            "name": "๖LL๖GàNhấtVN",
            "uid": uid,
            "level": 64,
            "exp": 1523259,
            "region": region.upper(),
            "likes": 19129,
            "honor_score": 100,
            "celebrity_status": False,
            "evo_access_badge": "Inactive",
            "title": "Not Found",
            "signature": "Rikaki Gaming"
        },
        "account_activity": {
            "most_recent_ob": "OB46",
            "fire_pass": "Basic",
            "current_bp_badges": "Not Found",
            "br_rank": "Bronze 1 (1000)",
            "cs_points": "undefined",
            "created_at": "04 December 2017 at 09:32:19",
            "last_login": "22 November 2024 at 08:03:22"
        },
        "account_overview": {
            "avatar_id": 902046033,
            "banner_id": 901046015,
            "pin_id": 910045001,
            "equipped_skills": ["Orion (P)", "Miguel (P)", "Shani (P)", "Antonio (P)"],
            "equipped_gun_id": 907104607,
            "equipped_animation_id": 912045002,
            "transform_animation_id": 914044001,
            "outfits": "Graphically Presented Below!"
        },
        "pet_details": {
            "equipped": True,
            "pet_name": "RiCàKhịa",
            "pet_type": "Raccoon",
            "pet_exp": 6000,
            "pet_level": 7
        },
        "guild_info": {
            "guild_name": "Ʀegeneration",
            "guild_id": 3034020316,
            "guild_level": 2,
            "live_members": 28,
            "leader_info": {
                "name": "_Runsain",
                "uid": 9773618119,
                "level": 1,
                "exp": 1,
                "created_at": "08 August 2024 at 07:59:48",
                "last_login": "04 April 2025 at 10:02:31",
                "title": "Not Found",
                "current_bp_badges": "Not Found",
                "br_points": 1000,
                "cs_points": "Not Found"
            }
        },
        "craftland_maps": "Not Found"
    })

if __name__ == '__main__':
    app.run(debug=True)
