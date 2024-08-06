from utils.TransactionDataDecoder import TransactionDataDecoder
from web3.logs import DISCARD
from web3 import Web3

class RoninTransactionDataDecoder(TransactionDataDecoder):

    # in all of these functions, we could receive as argument the receipt that we already have
    # however, to get the logs and call the `process_receipt` function we need the receipt as
    # an AtributeDict object which is seems to come directly from the Web3 package and I'm not
    # able to convert a normal dict object to such an object
    def decode_bridge_event_data(self, tx_hash, bridge_contract_abi, contract_address, index):
        try:
            (contract, receipt) = self.load_ABI_from_file(bridge_contract_abi, tx_hash, contract_address)

            logs = contract.events.TokenDeposited().process_receipt(receipt, errors=DISCARD)
            if len(logs) == 0:
                logs = contract.events.TokenWithdrew().process_receipt(receipt, errors=DISCARD)
            
            return logs[index].args
        except Exception as e:
            raise Exception("Could not decode bridge event data", tx_hash, e)

    def decode_bridge_v2_event_data(self, tx_hash, bridge_contract_abi, contract_address, index):
        try:
            (contract, receipt) = self.load_ABI_from_file(bridge_contract_abi, tx_hash, contract_address)

            logs = contract.events.Withdrew().process_receipt(receipt, errors=DISCARD)
            if len(logs) == 0:
                raise Exception("Invalid Operation")
            
            return logs[index].args
        except Exception as e:
            raise Exception("Could not decode bridge V2 event data", tx_hash, e)

