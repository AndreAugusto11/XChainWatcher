from utils.RoninTransactionDataDecoder import RoninTransactionDataDecoder
from utils.utils import convert_hex_to_int
from FactsExtractor import FactsExtractor
from utils.ronin_env import (
    SOURCE_CHAIN_BRIDGE_ADDRESS_V2,
    TARGET_CHAIN_CONNECTION_URL,
    TARGET_CHAIN_CONNECTION_OPTIONS,
    CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
    SOURCE_CHAIN_ID,
    SOURCE_CHAIN_ID,
    TARGET_CHAIN_ID,
    SOURCE_CHAIN_CONNECTION_URL,
    SOURCE_CHAIN_CONNECTION_OPTIONS,
    SOURCE_CHAIN_BRIDGE_ADDRESS,
    TARGET_CHAIN_BRIDGE_ADDRESS
)

class RoninFactsExtractor(FactsExtractor):

    def __init__(self, facts_folder):
        super().__init__(facts_folder)
        self.sc_transactionDecoder = RoninTransactionDataDecoder(SOURCE_CHAIN_CONNECTION_URL, SOURCE_CHAIN_CONNECTION_OPTIONS)
        self.tc_transactionDecoder = RoninTransactionDataDecoder(TARGET_CHAIN_CONNECTION_URL, TARGET_CHAIN_CONNECTION_OPTIONS)

    def sc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        deals_with_native_tokens = False

        if only_deposits or only_withdrawals:
            additional_data = True

        transaction_facts, erc20_transfer_facts, deposit_facts, withdrawal_facts, token_deposited_facts, token_withdrew_facts, _, errors = output_files

        #print("Extracting facts (Source Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        # this map allows us to keep track of the index of the event (not within the whole transaction, but emitted by contract interface)
        # this is necessary for decoding the logs of the transaction, and then knowing what is the current log based on the current index
        log_counter_map = {
            "bridge": 0,
            "nativeToken": 0,
            "erc20": 0
        }

        try:
            for idx, log in enumerate(transaction["logs"]):
                if log["address"] == SOURCE_CHAIN_BRIDGE_ADDRESS:

                    # TokenWithdrew(uint256,address,address,uint256)
                    if log["topics"][0].startswith("0x86174e"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction["transactionHash"], "utils/ABIs/ethereum/RONIN-BRIDGE-CONTRACT-ABI.json", log["address"].lower(), log_counter_map["bridge"])
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent['_withdrawId'], decodedEvent['_owner'].lower(), decodedEvent['_tokenAddress'].lower(), decodedEvent['_tokenNumber']))

                    # TokenDeposited(uint256,address,address,address,uint32,uint256)
                    elif log["topics"][0].startswith("0x728488"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction["transactionHash"], "utils/ABIs/ethereum/RONIN-BRIDGE-CONTRACT-ABI.json", log["address"].lower(), log_counter_map["bridge"])
                        token_deposited_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["_depositId"], decodedEvent['_owner'].lower(), decodedEvent['_sidechainAddress'].lower(), decodedEvent["_tokenAddress"].lower(), TARGET_CHAIN_ID, decodedEvent['_standard'], decodedEvent['_tokenNumber']))

                    log_counter_map["bridge"] += 1

                elif log["address"].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN:
                    deals_with_native_tokens = True

                    # Withdrawal(address,uint256)
                    if log["topics"][0].startswith("0x7fcf53"):
                        decodedEvent, user = self.sc_transactionDecoder.decode_weth_event_data(transaction["transactionHash"], "utils/ABIs/ethereum/RONIN-BRIDGE-CONTRACT-ABI.json", "utils/ABIs/ethereum/WETH-ABI.json", log["address"].lower(), log_counter_map["nativeToken"], "Withdrawal")
                        withdrawal_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["src"].lower(), user, decodedEvent["wad"]))

                    # Deposit(address,uint256)
                    elif log["topics"][0].startswith("0xe1fffc"):
                        decodedEvent, _ = self.sc_transactionDecoder.decode_weth_event_data(transaction["transactionHash"], "utils/ABIs/ethereum/RONIN-BRIDGE-CONTRACT-ABI.json", "utils/ABIs/ethereum/WETH-ABI.json", log["address"].lower(), log_counter_map["nativeToken"], "Deposit")
                        deposit_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, transaction["from"], decodedEvent["dst"].lower(), decodedEvent["wad"]))

                    log_counter_map["nativeToken"] += 1

                elif log["address"].lower() == SOURCE_CHAIN_BRIDGE_ADDRESS_V2 and additional_data:
                    
                    # Withdrew(bytes32,tuple)
                    if log["topics"][0].startswith("0x21e88e"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_v2_event_data(transaction["transactionHash"], "utils/ABIs/ethereum/RONIN-BRIDGE-CONTRACT-V2.json", log["address"].lower(), log_counter_map["bridge"])
                        receipt = decodedEvent["receipt"]
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, receipt['id'], receipt['mainchain']["addr"].lower(), receipt['mainchain']['tokenAddr'].lower(), receipt['info']["quantity"]))

                        if receipt['mainchain']['tokenAddr'].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN:
                            deals_with_native_tokens = True

                    log_counter_map["bridge"] += 1

                else: # there is the transfer of another token
                    decodedEvent = self.sc_transactionDecoder.decode_erc20_event_data(transaction["transactionHash"], "utils/ABIs/ERC20-ABI.json", log["address"].lower(), log_counter_map["erc20"])
                    self.store_erc20_fact(transaction, SOURCE_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                    log_counter_map["erc20"] += 1

            tx_value = 0
            # we want to extract the eth being transferred to the bridge if this is a transfer of native tokens through the bridge
            # or, transfers made directly to the bridge that do not emit events (just for stats)
            if deals_with_native_tokens or (not transaction["logs"] and convert_hex_to_int(transaction["status"])):
                # if we are dealing with native tokens we need to get the transaction value
                tx_value = self.sc_transactionDecoder.get_transaction(transaction["transactionHash"])["value"]

                if tx_value == 0 and deals_with_native_tokens:
                    tx_value = self.sc_transactionDecoder.debug_transaction_trace(transaction["transactionHash"])

            self.store_transaction_fact(blocks, SOURCE_CHAIN_ID, transaction, tx_value, transaction_facts)

        except Exception as e:
            errors.write("%s\t%s\n" % (transaction["transactionHash"], e))

    def tc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        additional_data = False

        if only_deposits or only_withdrawals:
            additional_data = True

        transaction_facts, erc20_transfer_facts, _, _, token_deposited_facts, token_withdrew_facts, _, errors = output_files

        #print("Extracting facts (Target Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        # this map allows us to keep track of the index of the event (not within the whole transaction, but emitted by contract interface)
        # this is necessary for decoding the logs of the transaction, and then knowing what is the current log based on the current index
        log_counter_map = {
            "bridge": 0,
            "erc20": 0
        }
        try:
            for idx, log in enumerate(transaction["logs"]):
                if log["address"] == TARGET_CHAIN_BRIDGE_ADDRESS:

                    # TokenWithdrew(uint256,address,address,address,uint32,uint256)
                    if log["topics"][0].startswith("0xd56c021e") and (only_withdrawals or not additional_data):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction["transactionHash"], "utils/ABIs/ronin/BRIDGE-ABI.json", log["address"].lower(), log_counter_map["bridge"])
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent['_withdrawId'], decodedEvent['_owner'].lower(), decodedEvent['_tokenAddress'].lower(), decodedEvent['_mainchainAddress'].lower(), SOURCE_CHAIN_ID, decodedEvent['_standard'], decodedEvent['_tokenNumber']))

                    # TokenDeposited(uint256,address,address,uint256)
                    if log["topics"][0].startswith("0x5187d31a") and (only_deposits or not additional_data):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction["transactionHash"], "utils/ABIs/ronin/BRIDGE-ABI.json", log["address"].lower(), log_counter_map["bridge"])
                        token_deposited_facts.write("%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["depositId"], decodedEvent['owner'].lower(), decodedEvent["tokenAddress"].lower(), decodedEvent['tokenNumber']))

                    log_counter_map["bridge"] += 1
                else: # there is the transfer of a token
                    # Transfer(address,address,uint256)
                    if log["topics"][0].startswith("0xddf252"):
                        decodedEvent = self.tc_transactionDecoder.decode_erc20_event_data(transaction["transactionHash"], "utils/ABIs/ERC20-ABI.json", log["address"].lower(), log_counter_map["erc20"])
                        self.store_erc20_fact(transaction, TARGET_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                        log_counter_map["erc20"] += 1
                    else:
                        # we can just ignore as this is another contract or an Approval event
                        pass

            self.store_transaction_fact(blocks, TARGET_CHAIN_ID, transaction, 0, transaction_facts) # In Ronin, the tx value is always 0

        except Exception as e:
            errors.write("%s\t%s\n" % (transaction["transactionHash"], e))
