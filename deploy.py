from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Compiling the solidity code.

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

print("Installing...")
install_solc("0.8.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# Deploy the compiled code

# get abi, bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# Connect to blockchain
ganache_chain_address = "http://127.0.0.1:8545"
infura_chain_address = os.getenv("RINKEBY_RPC_URL")
w3 = Web3(Web3.HTTPProvider(infura_chain_address))
# chain_id = 1337
chain_id = w3.eth.chain_id
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")



# Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract !!")
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print(f"Done. Contract deployed to {tx_receipt.contractAddress}")


# Working with deployed contracts
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial stored value: {simple_storage.functions.retrieve().call()}")
greeting_transaction = simple_storage.functions.store(20).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gasPrice,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_greeting_txn = w3.eth.account.signTransaction(
    greeting_transaction, private_key=private_key
)
sent_transaction = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(sent_transaction)

print(simple_storage.functions.retrieve().call())
