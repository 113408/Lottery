import pytest
from brownie import Lottery, accounts, config, network
from scripts.utils import get_interfaces, get_account
from web3 import Web3


def test_ticket_fee():
    """
    Test that the ticket fee is correctly set
    """
    account = get_account()
    interfaces = get_interfaces()
    lottery = Lottery.deploy(
        interfaces["price_feed"],
        50,
        2816,
        interfaces["key_hash"],
        interfaces["vrf_coordinator"],
        {"from": account},
    )
    assert lottery.getTicketFeeETH() > Web3.toWei(0.016, "ether")
    assert lottery.getTicketFeeETH() < Web3.toWei(0.020, "ether")


def test_buy_lottery_ticket():
    account = get_account()
    interfaces = get_interfaces()
    lottery = Lottery.deploy(
        interfaces["price_feed"],
        50,
        2816,
        interfaces["key_hash"],
        interfaces["vrf_coordinator"],
        {"from": account},
    )
    lottery.openLottery()
    tx = lottery.buyLotteryTicket(
        {"from": account, "amount": Web3.toWei(0.018, "ether")}
    )
    tx.wait(1)
    assert lottery.getMyLotteryTicketsNbr() == 1
    tx = lottery.buyLotteryTicket(
        {"from": account, "amount": Web3.toWei(0.018, "ether")}
    )
    tx.wait(1)
    assert lottery.getMyLotteryTicketsNbr() == 2


def test_close_lottery():
    owner = get_account()
    interfaces = get_interfaces()
    lottery = Lottery.deploy(
        interfaces["price_feed"],
        50,
        2816,
        interfaces["key_hash"],
        interfaces["vrf_coordinator"],
        {"from": owner},
    )
    lottery.openLottery()
    for i in range(1, 4):
        tx = lottery.buyLotteryTicket(
            {"from": accounts[i], "amount": Web3.toWei(0.018, "ether")}
        )
        tx.wait(1)
    lottery.closeLottery()
    assert accounts[1].balance == Web3.toWei(0.018, "ether") * 3
