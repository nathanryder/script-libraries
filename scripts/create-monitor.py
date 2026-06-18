import os
import sys
from dotenv import load_dotenv
import argparse

from uptime_kuma_api import UptimeKumaApi, UptimeKumaException, MonitorType


def parse_args():
    parser = argparse.ArgumentParser(
        prog="create-monitor.py",
        description="Create a monitor in Uptime Kuma."
    )
    parser.add_argument("name", help="The name of the monitor to create.", type=str)
    parser.add_argument("url", help="The URL of the monitor to create.", type=str)
    return parser.parse_args()


def load_config():
    load_dotenv()
    return {
        "url": os.getenv("UPTIME_KUMA_URL"),
        "username": os.getenv("UPTIME_KUMA_USER"),
        "password": os.getenv("UPTIME_KUMA_PASSWORD"),
    }


def create_monitor(api: UptimeKumaApi, name: str, url: str):
    api.add_monitor(
        type=MonitorType.HTTP,
        name=name,
        url=url,
        interval=120
    )
    print(f"Created monitor '{name}'")


if __name__ == "__main__":
    args = parse_args()
    config = load_config()

    try:
        api = UptimeKumaApi(config["url"])
        api.login(config["username"], config["password"])

        create_monitor(api, args.name, args.url)
    except UptimeKumaException as e:
        print(f"Uptime Kuma error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        api.disconnect()
