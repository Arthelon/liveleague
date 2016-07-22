import json
import os
import threading
import functools
import time

import click
import requests
from clint.textui import prompt
from config import API_KEY

avail_regions = ["BR", "EUNE", "EUW", "JP", "KR", "LAN", "LAS", "NA", "OCE", "RU", "TR"]
base_url = "https://na.api.pvp.net"
region = default_id = ""


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
                commands[choice-1]()
                time.sleep(2)    # delay before terminal clear
                click.clear()
    except (KeyboardInterrupt, click.exceptions.Abort):
        pass
    finally:
        click.echo("\nThanks for using liveleague!")


def view_match(summoner_id):
    pass


def load_defaults():
    global region, default_id

    with open("defaults.json", "r") as defaults_file:
        user_defaults = json.load(defaults_file)
        region = user_defaults["region"]
        default_id = user_defaults["summoner_id"]
    if not region:
        set_default_region()
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


def update_defaults():
    with open("defaults.json", "w") as defaults_file:
        json.dump({
            "summoner_id": default_id,
            "region": region
        }, defaults_file)


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


commands = [
    functools.partial(view_match, default_id),
    view_other_match,
    set_default_region,
    set_default_summoner_id
]


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