from abc import ABC, abstractmethod
from utils.utils import convert_hex_to_int
from web3.logs import DISCARD
from web3 import Web3
from enum import Enum
import requests
import json

class TransactionDataDecoder(ABC):

    def __init__(self, connection_url, connection_options):
        self.connection_url = connection_url
        self.connection_options = connection_options
        self.w3 = Web3(Web3.HTTPProvider(connection_url, request_kwargs=connection_options))

    def get_transaction(self, tx_hash):
        return self.w3.eth.get_transaction(tx_hash)

    def load_ABI_from_file(self, filename, tx_hash, contract_address):
        with open(filename, 'r') as f:
            abi = json.load(f)

        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)

        return (contract, receipt)

    # the WETH token only locks and unlocks tokens to the bridge, the user to whom the tokens are then transferred to
    # is not known only by looking at this event. So we will analyse the function call to retrieve the user
    def decode_weth_event_data(self, tx_hash, bridge_contract_abi, weth_contract_abi, weth_contract_address, index, event):
        try:
            (contract, receipt) = self.load_ABI_from_file(weth_contract_abi, tx_hash, weth_contract_address)
            logs = None
            user = None

            if event == "Transfer":
                logs = contract.events.Transfer().process_receipt(receipt, errors=DISCARD)
            elif event == "Deposit":
                logs = contract.events.Deposit().process_receipt(receipt, errors=DISCARD)
            elif event == "Withdrawal":
                logs = contract.events.Withdrawal().process_receipt(receipt, errors=DISCARD)
                
                if len(logs) > 0:
                    user = self.decode_transaction_data(bridge_contract_abi, self.get_transaction(tx_hash)["input"], weth_contract_address)[1]["_user"].lower()
            else:
                raise Exception("Invalid event provided")

            return (logs[index].args, user)
        except Exception as e:
            print("Could not decode WETH event data", e)

    def decode_erc20_event_data(self, tx_hash, erc20_contract_abi, contract_address, index):
        try:
            (contract, receipt) = self.load_ABI_from_file(erc20_contract_abi, tx_hash, contract_address)

            logs = contract.events.Transfer().process_receipt(receipt, errors=DISCARD)

            return logs[index].args
        except Exception as e:
            print("Could not decode ERC20 event data", e)

    def decode_transaction_data(self, contract_abi_filename, data, contract_address):
        with open(contract_abi_filename, 'r') as f:
            bridge_contract_abi = json.load(f)

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=bridge_contract_abi)

        try:
            return contract.decode_function_input(data)
        except Exception as e:
            print("Could not decode transaction data", e)

    def debug_transaction_trace(self, tx_hash):
        # it seems like the debug.traceTransaction method is not available in the Web3 api, so we will do a direct http request
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "params": [tx_hash, {"tracer": "callTracer"}],
            "method": "debug_traceTransaction"
        }

        response = requests.post(self.connection_url, headers=self.connection_options["headers"], data=json.dumps(data))

        trace = response.json()["result"]

        for call in trace["calls"]:
            value = self.process_call(call)
            return convert_hex_to_int(value)

    def process_call(self, call):
        try:
            value = call["value"]
            
            if value != "0x0":
                return value
        except Exception as e:
            pass
        
        try:
            for c in call["calls"]:
                value = self.process_call(c)
                if value != None:
                    return value
        except Exception as e:
            pass

    @abstractmethod
    def decode_bridge_event_data(self, tx_hash, bridge_contract_abi, index):
        pass
