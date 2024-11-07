from abc import ABC, abstractmethod
from utils.TransactionDataDecoder import TransactionDataDecoder
from utils.utils import convert_hex_to_int
import shutil
import os

class FactsExtractor(ABC):

    def __init__(self, facts_folder, evaluation_folder):
        self.facts_folder = facts_folder
        self.evaluation_folder = evaluation_folder

        try:
            if os.path.exists(self.facts_folder):
                shutil.rmtree(self.facts_folder, ignore_errors=True)
            
            os.makedirs(self.facts_folder)

            if os.path.exists(self.evaluation_folder):
                shutil.rmtree(self.evaluation_folder, ignore_errors=True)

            os.makedirs(self.evaluation_folder)

        except:
            raise Exception("Not able to open file")

    @abstractmethod
    def sc_extract_facts_from_transaction(self, transaction, blocks, only_deposits, only_withdrawals):
        pass

    @abstractmethod
    def tc_extract_facts_from_transaction(self, transaction, blocks, only_deposits, only_withdrawals):
        pass

    def store_transaction_fact(self, blocks, chain_id, transaction, tx_value, transaction_facts):
        timestamp = blocks.get(int(transaction["blockNumber"], 16))
        tx_fee_eth = int(transaction["gasUsed"], 16) * int(transaction["effectiveGasPrice"], 16)
        transaction_facts.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%s\r\n" % (timestamp, chain_id, transaction["transactionHash"], convert_hex_to_int(transaction["transactionIndex"]), transaction["from"], transaction["to"], tx_value, convert_hex_to_int(transaction["status"]), tx_fee_eth))

    def store_erc20_fact(self, transaction, chain_id, idx, log, erc20_transfer_facts, _from, _to, _value):
        erc20_transfer_facts.write("%s\t%d\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], chain_id, idx, log["address"], _from, _to, _value))
