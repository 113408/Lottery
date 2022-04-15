from scripts.utils import get_interfaces, get_account
from brownie import Lottery, config, network


def deploy():
    account = get_account()
    interfaces = get_interfaces()
    lottery = Lottery.deploy(
        interfaces["price_feed"],
        50,
        2816,
        interfaces["key_hash"],
        interfaces["vrf_coordinator"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Lottery contract deployed to: {lottery.address}")


def main():
    deploy()
