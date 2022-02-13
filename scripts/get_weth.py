from brownie import interface, config, network
from scripts.helpful_scripts import get_account


def get_weth():
    """
    Mints WETH by depositing ETH.

    """
    account = get_account()
    weth = interface.IWETH(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print(f"Received 0.1 WETH")
    return tx


def main():
    get_weth()
