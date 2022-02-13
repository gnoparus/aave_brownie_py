from threading import local
from brownie import interface, config, network
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print(f"Approving ERC-20 Token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print(f"Approved!!")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account)
    print(f"totalCollateralETH = {totalCollateralETH}")
    print(f"totalDebtETH = {totalDebtETH}")
    print(f"availableBorrowsETH = {availableBorrowsETH}")
    print(f"currentLiquidationThreshold = {currentLiquidationThreshold}")
    print(f"ltv = {ltv}")
    print(f"healthFactor = {healthFactor}")

    return (
        float(Web3.fromWei(availableBorrowsETH, "ether")),
        float(Web3.fromWei(totalDebtETH, "ether")),
    )


def get_asset_price(price_feed_address):
    pricefeed = interface.AggregatorV3Interface(price_feed_address)
    price = pricefeed.latestRoundData()[1]
    print(f"price = {price}")
    priceEth = float(Web3.fromWei(price, "ether"))
    print(f"priceEth = {priceEth}")
    return priceEth


## 0.1
AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]

    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        get_weth()

    lending_pool = get_lending_pool()
    print(lending_pool)

    ## Approve sending ERC-20 Tokens
    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    print(f"Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print(f"Deposited")
    (availableBorrowsETH, totalDebtETH) = get_borrowable_data(lending_pool, account)
    print(
        f"(availableBorrowsETH, totalDebtETH) = {(availableBorrowsETH, totalDebtETH)}"
    )

    print(f" Let's borrow!!")
    ### DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
