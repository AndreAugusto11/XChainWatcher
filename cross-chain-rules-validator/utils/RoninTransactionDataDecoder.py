from utils.TransactionDataDecoder import TransactionDataDecoder
from web3.datastructures import AttributeDict

class RoninTransactionDataDecoder(TransactionDataDecoder):

    def decode_bridge_event_data(self, receipt, bridge_contract_abi, contract_address, index, event):
        try:
            contract = self.load_ABI_from_file(bridge_contract_abi, contract_address)

            log = receipt['logs'][index]
            
            if event == "Deposit":
                decoded_log = contract.events.TokenDeposited().process_log(log)
            elif event == "Withdrawal":
                decoded_log = contract.events.TokenWithdrew().process_log(log)
            else:
                raise Exception("Invalid Operation")

            return AttributeDict(decoded_log['args'])
        except Exception as e:
            raise Exception(f"Could not decode bridge event data ({event}), (index: {index})", receipt["transactionHash"], e)

    def decode_bridge_v2_event_data(self, receipt, bridge_contract_abi, contract_address, index):
        try:
            contract = self.load_ABI_from_file(bridge_contract_abi, contract_address)

            log = receipt['logs'][index]
            
            decoded_log = contract.events.Withdrew().process_log(log)
            
            return AttributeDict(decoded_log['args'])
        except Exception as e:
            raise Exception("Could not decode bridge V2 event data", receipt["transactionHash"], e)

