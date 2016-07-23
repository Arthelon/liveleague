import json
import threading
import time
import pprint

import click
import requests
from clint.textui import prompt
from config import API_KEY

avail_regions = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "ru", "tr"]
api_url = "https://{:s}.api.pvp.net"  # interpolated to region
global_api_url = "https://global.api.pvp.net"
region = ""
default_id = ""


def run():
    try:
        load_defaults()
        click.clear()

        # main loop
        while True:
            choice = prompt.options("What would you like to do?: ", [
                "Find live match of default summoner",
                "Find live match of another summoner",
                "Change default region",
                "Change default summoner",
                "Quit"
            ])
            if choice == 5:
                break
            else:
                commands[choice - 1]()
                time.sleep(2)  # delay before terminal clear
                # click.clear()
    except (KeyboardInterrupt, click.exceptions.Abort):
        pass
    finally:
        click.echo("\nThanks for using liveleague!")


def view_match(summoner_id=None):
    if not summoner_id:
        summoner_id = default_id
    match_details = get_match_details(summoner_id)
    if not match_details:
        click.echo("Summoner is not in game")
        return
    players = match_details["participants"]
    map_id = match_details["mapId"]
    click.echo("Match found!")
    map_name = get_map_name(map_id)
    summoner_data = get_summoner_data(players, summoner_id)
    display_summoners(summoner_data)


def display_summoners(data):
    pass


def get_summoner_data(summoners, target_id):
    allied_id = get_team_id(summoners, target_id)
    live_data = {summoner["summonerId"]: summoner for summoner in summoners}
    print("Loading data of other summoners...")
    summoner_data = {"allies": {}, "enemies": {}}
    for s_id, data in live_data.items():
        key = "enemies"
        if data["teamId"] == allied_id:
            key = "allies"
        summoner_data[key][s_id] = {
            "champion_id": live_data[s_id]["championId"],
            "summoner_name": live_data[s_id]["summonerName"]
        }
    thread_list = []
    for team in summoner_data.keys():
        for summoner_id in summoner_data[team].keys():
            pass #get data
    for thread in thread_list:
        thread.join()

    return summoner_data


def get_team_id(summoners_list, target_id):
    for summoner in summoners_list:
        if summoner["summonerId"] == target_id:
            return summoner["teamId"]
    return 0


def get_map_name(map_id):
    try:
        resp = requests.get(global_api_url + "/api/lol/static-data/{:s}/v1.2/map".format(region),
                            params={"api_key": API_KEY})
        resp.raise_for_status()
        return resp.json()["data"][str(map_id)]["mapName"]
    except requests.HTTPError:
        error("Error occurred while retrieving map name")


def get_match_details(summoner_id):
    try:
        resp = requests.get(api_url + "/observer-mode/rest/consumer/getSpectatorGameInfo/{:s}/{:d}".format(
            region.upper() + "1",  # NA => NA1, EUNE => EUNE1 etc...
            summoner_id), params={"api_key": API_KEY})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError:
        error("Error while retrieving match details")


def load_defaults():
    global region, default_id, api_url

    with open("defaults.json", "r") as defaults_file:
        user_defaults = json.load(defaults_file)
        region = user_defaults["region"]
        default_id = user_defaults["summoner_id"]
    if not region:
        set_default_region()
    else:
        update_api_url()
    if not default_id:
        set_default_summoner_id()


def set_default_summoner_id():
    global default_id
    summoner = click.prompt("Please enter default summoner handle", type=click.STRING)
    default_id = get_summoner_id(summoner)
    while not default_id:
        print("Was not able to find summoner: {:s}\n".format(summoner))
        summoner = click.prompt("Please enter default summoner handle", type=click.STRING)
        default_id = get_summoner_id(summoner)
    click.echo("Default summoner changed to: {:s}".format(summoner))
    update_defaults()


def set_default_region():
    global region
    region = click.prompt("Please enter default server region", type=click.Choice(avail_regions))
    click.echo("Default region changed to: {:s}".format(region))
    update_defaults()


def update_api_url():
    global api_url
    api_url = api_url.format(region)


def update_defaults():
    update_api_url()
    with open("defaults.json", "w") as defaults_file:
        json.dump({
            "summoner_id": default_id,
            "region": region
        }, defaults_file)


def get_summoner_id(handle):
    try:
        resp = requests.get(api_url + "/api/lol/{:s}/v1.4/summoner/by-name/{:s}".format(region, handle), params={
            "api_key": API_KEY})
        if resp.status_code == 404:
            return ""
        return resp.json()[normalize_name(handle)]["id"]
    except requests.HTTPError:
        error("Error while getting summoner")
    return ""


def view_other_match():
    summoner = click.prompt("Please enter summoner handle", type=click.STRING)
    summoner_id = get_summoner_id(summoner)
    while not summoner_id:
        print("Was not able to find summoner: {:s}\n".format(summoner))
        summoner = click.prompt("Please enter summoner handle", type=click.STRING)
        summoner_id = get_summoner_id(summoner)
    view_match(summoner_id)


def error(msg):
    click.echo(msg)
    exit(1)


def normalize_name(name):
    return "".join(name.split(" ")).lower()


commands = [
    view_match,
    view_other_match,
    set_default_region,
    set_default_summoner_id
]

if __name__ == "__main__":
    run()
