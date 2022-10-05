import datetime
import re
import sys
import time
from typing import Optional

import requests
import toml


def update_bio(
    cookie: str,
    description: str,
    pin: Optional[str] = None,
):
    with requests.Session() as session:
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
            }
        )
        session.cookies.set(".ROBLOSECURITY", cookie, domain="roblox.com")
        userinfo = session.get("https://www.roblox.com/mobileapi/userinfo")

        if userinfo.status_code != 200:
            sys.exit("Unable to login, please check cookie")

        userinfo_data = userinfo.json()
        name = userinfo_data["UserName"]
        robux = userinfo_data["RobuxBalance"]
        print(f"Logged in to {name}. \nCurrent robux: {robux}")

        home = session.get("https://www.roblox.com/home")

        if home.status_code != 200:
            sys.exit(
                f"Something went wrong, try again later. Status code: {home.status_code}"
            )

        csrf_token = re.search(r'data-token="?([\w/\-\+]+)"?', home.text)

        if csrf_token:
            session.headers.update({"X-CSRF-TOKEN": csrf_token.group(1)})

        if pin:
            pin_response = session.post(
                "https://auth.roblox.com/v1/account/pin/unlock",
                data={"pin": pin, "reauthenticationToken": "string"},
            )
            if pin_response.status_code != 200:
                sys.exit(
                    f"Something went wrong, try again later. Status code: {home.status_code}"
                )

            print("unlocked pin")

        description = re.sub(r"%robux%", f"{robux:,}", description)

        description_response = session.post(
            "https://accountinformation.roblox.com/v1/description",
            data={"description": description},
        )

        if description_response.status_code != 200:
            sys.exit(
                f"Something went wrong, try again later. Status code: {home.status_code}"
            )

        print(f"updated {datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}")

        if pin:
            pin_response = session.post("https://auth.roblox.com/v1/account/pin/lock")

            if pin_response.status_code != 200:
                sys.exit(
                    f"Something went wrong, try again later. Status code: {home.status_code}"
                )

            print("locked pin")


if __name__ == "__main__":
    config = toml.load("config.toml")

    cookie = config["cookie"].split("|_")[-1]
    if not re.match("[A-F0-9]{100,1000}$", cookie):
        sys.exit("cookie format is not valid")

    pin = config["pin"] if config["pin"] != "" else None

    while True:
        update_bio(cookie=cookie, description=config["description"], pin=pin)
        time.sleep(config["update_delay"])
