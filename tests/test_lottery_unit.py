import pytest
from brownie import accounts, network
from scripts.utils import get_interfaces, get_account
from web3 import Web3
from scripts.deploy import deploy


@pytest.fixture
def account():
    return get_account()


@pytest.fixture
def interfaces():
    return get_interfaces()


@pytest.fixture
def lottery(account):
    return deploy(account)


def test_ticket_fee(lottery):
    """
    Test that the ticket fee is correctly set
    """
    assert lottery.getTicketFeeETH() > Web3.toWei(0.016, "ether")
    assert lottery.getTicketFeeETH() < Web3.toWei(0.020, "ether")


def test_buy_lottery_ticket(lottery):
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


def test_random_winner(lottery, interfaces, account):
    lottery.openLottery()
    starting_balance = accounts[0].balance
    for i in range(1, 9):
        tx = lottery.buyLotteryTicket(
            {"from": accounts[i], "amount": Web3.toWei(0.018, "ether")}
        )
        tx.wait(1)
    tx = lottery.closeLottery()
    request_id = tx.event["ClosingLottery"]
    vrf_coordinator = interfaces["vrf_coordinator"]
    vrf_coordinator.fulfillRandomWords(request_id, lottery.address, {"from": account})
    assert lottery.s_randomWords(0) > 0
    assert accounts[lottery.winnerIndex()].balance > starting_balance


def test_close_lottery(lottery):
    lottery.openLottery()
    assert lottery.getLotteryState() == lottery.STATE.OPEN
    lottery.closeLottery()
    assert lottery.getLotteryState() == lottery.STATE.CLOSED
    assert accounts[1].balance() == Web3.toWei(0.018, "ether") * 9
