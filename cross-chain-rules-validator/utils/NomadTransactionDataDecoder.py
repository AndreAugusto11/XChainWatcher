from utils.TransactionDataDecoder import TransactionDataDecoder
from web3.datastructures import AttributeDict
from web3.logs import DISCARD

class NomadTransactionDataDecoder(TransactionDataDecoder):

    # in all of these functions, we could receive as argument the receipt that we already have
    # however, to get the logs and call the `process_receipt` function we need the receipt as
    # an AtributeDict object which is seems to come directly from the Web3 package and I'm not
    # able to convert a normal dict object to such an object
    def decode_bridge_event_data(self, receipt, bridge_contract_abi, contract_address, index, event):
        try:
            contract = self.load_ABI_from_file(bridge_contract_abi, contract_address)
            
            log = receipt["logs"][index]
            
            if event == "Deposit":
                decoded_log = contract.events.Send().process_log(log)
            elif event == "Withdrawal":
                decoded_log = contract.events.Receive().process_log(log)
            else:
                raise Exception("Invalid Operation")
            
            return AttributeDict(decoded_log['args'])
        except Exception as e:
            raise Exception("Could not decode bridge event data", receipt["transactionHash"], e)


    def decode_home_contract_event_data(self, receipt, bridge_contract_abi, contract_address, index):
        try:
            contract = self.load_ABI_from_file(bridge_contract_abi, contract_address)
            
            log = receipt["logs"][index]

            decoded_log = contract.events.Dispatch().process_log(log)
            
            return AttributeDict(decoded_log['args'])
        except Exception as e:
            raise Exception("Could not decode home event data", receipt["transactionHash"], e)
