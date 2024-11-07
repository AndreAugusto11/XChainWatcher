from abc import ABC, abstractmethod
from utils.utils import convert_hex_to_int
from web3.datastructures import AttributeDict
from web3.logs import DISCARD
from web3 import Web3
import requests
import json
import time
import os

class TransactionDataDecoder(ABC):

    def __init__(self, connection_url, connection_options):
        self.connection_url = connection_url
        self.connection_options = connection_options
        self.w3 = Web3(Web3.HTTPProvider(connection_url, request_kwargs=connection_options))

    def get_transaction(self, tx_hash):
        return self.w3.eth.get_transaction(tx_hash)

    def load_ABI_from_file(self, filename, contract_address):
        with open(filename, 'r') as f:
            abi = json.load(f)

        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

        return contract

    # the WETH token only locks and unlocks tokens to the bridge, the user to whom the tokens are then transferred to
    # is not known only by looking at this event. So we will analyse the function call to retrieve the user
    def decode_weth_event_data(self, receipt, bridge_contract_abi, weth_contract_abi, weth_contract_address, index, event):
        try:
            contract = self.load_ABI_from_file(weth_contract_abi, weth_contract_address)
            decoded_log = None
            user = None

            log = receipt["logs"][index]

            if event == "Transfer":
                decoded_log = contract.events.Transfer().process_log(log)
            elif event == "Deposit":
                decoded_log = contract.events.Deposit().process_log(log)
            elif event == "Withdrawal":
                decoded_log = contract.events.Withdrawal().process_log(log)
                
                user = self.decode_transaction_data(bridge_contract_abi, self.get_transaction(receipt["transactionHash"])["input"], weth_contract_address)[1]["_user"].lower()
            else:
                raise Exception("Invalid event provided")

            return (AttributeDict(decoded_log['args']), user)
        except Exception as e:
            raise Exception("Could not decode WETH event data", e)

    def decode_erc20_event_data(self, receipt, erc20_contract_abi, contract_address, index):
        try:
            contract = self.load_ABI_from_file(erc20_contract_abi, contract_address)

            log = receipt["logs"][index]

            decoded_log = contract.events.Transfer().process_log(log)

            return AttributeDict(decoded_log['args'])
        except Exception as e:
            raise Exception("Could not decode ERC20 event data", e)

    def decode_transaction_data(self, contract_abi_filename, data, contract_address):
        contract = self.load_ABI_from_file(contract_abi_filename, contract_address)

        try:
            return contract.decode_function_input(data)
        except Exception as e:
            raise Exception("Could not decode transaction data", e)

    def debug_transaction_trace(self, tx_hash, max_retries=7, initial_delay=1):
        # it seems like the debug.traceTransaction method is not available in the Web3 api, so we will do a direct http request
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "params": [tx_hash, {"tracer": "callTracer"}],
            "method": "debug_traceTransaction"
        }

        attempt = 0
        delay = initial_delay

        while attempt < max_retries:
            try:
                response = requests.post(self.connection_url, headers=self.connection_options["headers"], data=json.dumps(data))

                response.raise_for_status()
                trace = response.json().get("result")

                if trace is not None:
                    for call in trace["calls"]:
                        value = self.process_call(call)
                        return convert_hex_to_int(value)
                else:
                    raise Exception("No result found in the response")

            except Exception as e:
                attempt += 1

                if attempt == max_retries:
                    raise Exception("Could not debug transaction trace", e, response.json() if response else None)

                time.sleep(delay)
                delay *= 2

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
    def decode_bridge_event_data(self, receipt, bridge_contract_abi, index):
        pass
