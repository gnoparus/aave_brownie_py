from filecmp import DEFAULT_IGNORES

from brownie import (
    network,
    config,
    accounts,
    interface,
    Contract,
)
from web3 import Web3


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8
INITIAL_VALUE = 3200 * 10**DECIMALS


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # use generaged fake account
        return accounts[0]

    # use mm account saved in brownie-config
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        # MockV3Aggregator[-1 ] , VRFCoordinatorMock , LinkToken
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract

    # return {        _priceFeedAddress,
    #      _vrfCoordinator,
    #      _link,
    #      _fee,
    #      _keyHash,
    #     "from": account}


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = account if account else get_account()

    ### using mock contract
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})

    ### using mock interface
    # link_token_smartcontract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_smartcontract.transfer(contract_address, amount, {"from": account})

    tx.wait(1)
    print("Fund contract!")
    return tx
