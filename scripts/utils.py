from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
)


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]
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
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


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
    print("Mocks deployed successfully.")


# TODO remove the hardcoded network on key_hash
def get_interfaces():
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        deploy_mocks()
        return {
            "price_feed": MockV3Aggregator[-1].address,
            "vrf_coordinator": VRFCoordinatorV2Mock[-1].address,
            "key_hash": config["networks"]["mainnet-fork"]["key_hash"],
        }
    else:
        return {
            "price_feed": config["networks"][network.show_active()][
                "eth_usd_price_feed"
            ],
            "vrf_coordinator": config["networks"][network.show_active()][
                "vrf_coordinator"
            ],
            "key_hash": config["networks"]["mainnet-fork"]["key_hash"],
        }
