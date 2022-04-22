from scripts.utils import (
    get_interfaces,
    get_account,
    LOCAL_BLOCKHAIN_ENVIRONMENTS,
    FORKED_LOCAL_ENVIRONMENTS,
)
from brownie import Lottery, config, network, convert, accounts


def create_subscription(account, vrf_coordinator):
    print("Creating subscription...")
    tx = vrf_coordinator.createSubscription({"from": account})
    tx.wait(1)
    subscription_id = tx.events[0]["subId"]
    print(f"Subscription created with id: {subscription_id}")
    return subscription_id


def fund_subscription(account, vrf_coordinator, subscription_id, link_token):
    print("Funding subscription...")
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        tx = vrf_coordinator.fundSubscription(
            subscription_id, 1000000000000000000, {"from": account}
        )
        tx.wait(1)
    else:
        tx = link_token.transferAndCall(
            vrf_coordinator.address,
            1000000000000000000,
            convert.to_bytes(subscription_id),
            {"from": account},
        )
        tx.wait(1)
    print("Subscription funded")


def update_lottery_subscription(account, subscription_id, lottery):
    print("Seting the contract subscription id...")
    tx = lottery.setSubscription(subscription_id, {"from": account})
    tx.wait(1)
    print("Contract subscription updated successfully")


def add_consumer(account, vrf_coordinator, lottery, subscription_id):
    subscription_details = vrf_coordinator.getSubscription(subscription_id)
    if lottery in subscription_details[3]:
        print(f"{lottery} is already in the subscription")
    else:
        print(f"Adding consumer to subscription {subscription_id} on address {lottery}")
        tx = vrf_coordinator.addConsumer.transact(
            subscription_id, lottery.address, {"from": account}
        )
        tx.wait(1)
        print("Consumer added to subscription!")


def setup_coordinator(account, vrf_coordinator, lottery, link_token):
    if (
        network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        subscription_id = create_subscription(account, vrf_coordinator)
        fund_subscription(account, vrf_coordinator, subscription_id, link_token)
    else:
        subscription_id = config["networks"][network.show_active()]["sub_id"]
    update_lottery_subscription(account, subscription_id, lottery)
    add_consumer(account, vrf_coordinator, lottery, subscription_id)


def deploy(account):
    interfaces = get_interfaces()
    vrf_coordinator = interfaces["vrf_coordinator"]
    link_token = interfaces["link_token"]
    lottery = Lottery.deploy(
        interfaces["price_feed"].address,
        50,
        interfaces["key_hash"],
        vrf_coordinator.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Lottery contract deployed to: {lottery.address}")
    setup_coordinator(account, vrf_coordinator, lottery, link_token)
    return lottery


def start_lottery(account, lottery):
    tx = lottery.openLottery({"from": account})
    tx.wait(1)
    print("Lottery is open!")


def buy_lottery_ticket(account, lottery):
    print(
        f"Current account balance {account.balance()} and the ticket price is {lottery.getTicketFeeETH()}"
    )
    tx = lottery.buyLotteryTicket({"from": account, "value": lottery.getTicketFeeETH()})
    tx.wait(1)
    print("Ticket bought!")


def close_lottery(account, lottery):
    tx = lottery.closeLottery({"from": account})
    tx.wait(1)
    print("The lottery has closed!")


def main():
    account = get_account()
    lottery = deploy(account)
    start_lottery(account, lottery)
    for ac in accounts:
        buy_lottery_ticket(ac, lottery)
    print(f"I have {lottery.getMyLotteryTicketsNbr()} tickets")
    close_lottery(account, lottery)
