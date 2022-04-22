from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    LinkToken,
    Contract,
)


FORKED_LOCAL_ENVIRONMENTS = [
    "mainnet-fork",
    "mainnet-fork-infura",
    "rinkeby-fork-infura",
]
LOCAL_BLOCKHAIN_ENVIRONMENTS = ["ganache-local", "development"]


DECIMALS = 8
STARTING_PRICE = 300000000000
BASE_FEE = 1000
GAS_PRICE_LINK = 100


def get_account():
    if (
        network.show_active() in FORKED_LOCAL_ENVIRONMENTS
        or network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS
    ):
        account = accounts[0]
    else:
        account = accounts.add(config["wallets"]["from_key"])
    print(
        f"The used account is: {account.address} and the balance is {account.balance()}"
    )
    return account


def deploy_mocks():
    print("Deploying mocks...")
    account = get_account()
    if len(MockV3Aggregator) == 0:
        print("Deploying MockAggregatorV3Interface")
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
        print("MockAggregatorV3Interface deployed successfully.")
    if len(VRFCoordinatorV2Mock) == 0:
        print("Deploying VRFCoordinatorV2Mock")
        VRFCoordinatorV2Mock.deploy(BASE_FEE, GAS_PRICE_LINK, {"from": account})
        print("VRFCoordinatorV2Mock deployed successfully.")
    if len(LinkToken) == 0:
        print("Deploying LinkToken")
        LinkToken.deploy({"from": account})
        print("LinkToken deployed successfully.")
    print("Mocks deployed successfully.")
    mocks = {
        "price_feed": MockV3Aggregator[-1],
        "vrf_coordinator": VRFCoordinatorV2Mock[-1],
        "link_token": LinkToken[-1],
        "key_hash": config["networks"]["mainnet-fork"]["key_hash"],
    }
    print(f"Mocks: {mocks}")
    return mocks


def get_interfaces():
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        return deploy_mocks()
    else:
        return {
            "price_feed": Contract.from_abi(
                MockV3Aggregator._name,
                config["networks"][network.show_active()]["eth_usd_price_feed"],
                abi=MockV3Aggregator.abi,
            ),
            "vrf_coordinator": Contract.from_abi(
                VRFCoordinatorV2Mock._name,
                config["networks"][network.show_active()]["vrf_coordinator"],
                abi=VRFCoordinatorV2Mock.abi,
            ),
            "link_token": Contract.from_abi(
                LinkToken._name,
                config["networks"][network.show_active()]["link_token"],
                abi=LinkToken.abi,
            ),
            "key_hash": config["networks"][network.show_active()]["key_hash"],
        }
