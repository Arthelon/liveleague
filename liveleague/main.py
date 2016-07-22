import json
import os
import threading

import click
import requests
from config import API_KEY

avail_regions = ["BR", "EUNE", "EUW", "JP", "KR", "LAN", "LAS", "NA", "OCE", "RU", "TR"]
base_url = "https://na.api.pvp.net"
region = ""


def run():
    global region

    with open("defaults.json", "r") as defaults_file:
        user_defaults = json.load(defaults_file)
        region = user_defaults["region"]
        summoner_id = user_defaults["summoner_id"]
    if not region:
        region = get_default_region()
    if not summoner_id:
        summoner_id = get_default_summoner_id()

    # Update user defaults file
    with open("defaults.json", "w") as defaults_file:
        json.dump({
            "summoner_id": summoner_id,
            "region": region
        }, defaults_file)


def get_default_summoner_id():
    summoner = click.prompt("Please enter default summoner handle", type=click.STRING)
    summoner_id = get_summoner_id(summoner)
    while not id:
        summoner = click.prompt("Please enter default summoner handle", type=click.STRING)
        summoner_id = get_summoner_id(summoner)
    return summoner_id


def get_default_region():
    return click.prompt("Please enter default server region", type=click.Choice(avail_regions))


def get_summoner_id(handle):
    try:
        resp = requests.get(base_url+"/api/lol/{:s}/v1.4/summoner/by-name/{:s}".format(region, handle), params={
            "api_key": API_KEY})
        if resp.status_code == 404:
            return ""
        return resp.json()[handle]["id"]
    except requests.HTTPError:
        error("Error while getting summoner")
    return ""


def error(msg):
    print(msg)
    exit(1)


if __name__ == "__main__":
    run()


### Specification
"""
- Specify default summoner and region if not found
- Options screen selecting between
    + Changing default summoner
    + Changing default region
    + Viewing live match details of default summoner
    + Viewing live match details of another summoner

"""