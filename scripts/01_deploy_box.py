from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    network,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)
import time


def depl_boxV1():
    account = get_account()
    print(f"Deploying to {network.show_active()}!")
    box = Box.deploy({"from": account}, publish_source=True)
    # Hooking up a proxy/proxyAdmin to our implementation contract.

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)
    # We need to encode(to bytes) the initializer fxn
    # initializer = box.store, 1 ... [Challenge to use an initialiser implementation after]
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )

    print(f"Proxy has been deployed to {proxy} , @dev can now upgrade contract to V2! ")
    # Now we always want to call these functions thriugh the proxy and not directly
    # @dev assigns the proxy address the abi of the Box contract.
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # Now we're going to upgrade the implementation contract to the BoxV2, @dev starts by deploying BoxV2
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    # upgrade
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())

    time.sleep(1)


def main():
    depl_boxV1()
