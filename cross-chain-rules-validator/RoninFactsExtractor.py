from utils.RoninTransactionDataDecoder import RoninTransactionDataDecoder
from utils.utils import convert_hex_to_int, convert_topics_to_hex
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
    TARGET_CHAIN_BRIDGE_ADDRESS,
    ABIs_DIR,
    SC_ABIs_DIR,
    TC_ABIs_DIR,
)

class RoninFactsExtractor(FactsExtractor):

    def __init__(self, facts_folder, evaluation_folder):
        super().__init__(facts_folder, evaluation_folder)
        self.sc_transactionDecoder = RoninTransactionDataDecoder(SOURCE_CHAIN_CONNECTION_URL, SOURCE_CHAIN_CONNECTION_OPTIONS)
        self.tc_transactionDecoder = RoninTransactionDataDecoder(TARGET_CHAIN_CONNECTION_URL, TARGET_CHAIN_CONNECTION_OPTIONS)

    def sc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        deals_with_native_tokens = False
        additional_data = False

        if only_deposits or only_withdrawals:
            additional_data = True

        transaction_facts, erc20_transfer_facts, deposit_facts, withdrawal_facts, token_deposited_facts, token_withdrew_facts, _, errors = output_files

        #print("Extracting facts (Source Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        # this map allows us to keep track of the index of the event (not within the whole transaction, but emitted by contract interface)
        # this is necessary for decoding the logs of the transaction, and then knowing what is the current log based on the current index

        try:
            for idx, log in enumerate(transaction["logs"]):
                convert_topics_to_hex(log)
                if log["address"] == SOURCE_CHAIN_BRIDGE_ADDRESS:

                    # TokenWithdrew(uint256,address,address,uint256)
                    if log["topics"][0].hex().startswith("86174e"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-ABI.json", log["address"].lower(), idx, "Withdrawal")
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent['_withdrawId'], decodedEvent['_owner'].lower(), decodedEvent['_tokenAddress'].lower(), decodedEvent['_tokenNumber']))

                    # TokenDeposited(uint256,address,address,address,uint32,uint256)
                    elif log["topics"][0].hex().startswith("728488"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-ABI.json", log["address"].lower(), idx, "Deposit")
                        token_deposited_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["_depositId"], decodedEvent['_owner'].lower(), decodedEvent['_sidechainAddress'].lower(), decodedEvent["_tokenAddress"].lower(), TARGET_CHAIN_ID, decodedEvent['_standard'], decodedEvent['_tokenNumber']))

                elif log["address"].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN:

                    # Withdrawal(address,uint256)
                    if log["topics"][0].hex().startswith("7fcf53") and (only_withdrawals or not additional_data):
                        deals_with_native_tokens = True
                        decodedEvent, user = self.sc_transactionDecoder.decode_weth_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-ABI.json", SC_ABIs_DIR + "WETH-ABI.json", log["address"].lower(), idx, "Withdrawal")
                        withdrawal_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["src"].lower(), user, decodedEvent["wad"]))

                    # Deposit(address,uint256)
                    elif log["topics"][0].hex().startswith("e1fffc") and (only_deposits or not additional_data):
                        deals_with_native_tokens = True
                        decodedEvent, _ = self.sc_transactionDecoder.decode_weth_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-ABI.json", SC_ABIs_DIR + "WETH-ABI.json", log["address"].lower(), idx, "Deposit")
                        deposit_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, transaction["from"], decodedEvent["dst"].lower(), decodedEvent["wad"]))

                    # Transfer(address,address,uint256)
                    elif log["topics"][0].hex().startswith("ddf252"):
                        decodedEvent, _ = self.sc_transactionDecoder.decode_weth_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-ABI.json", SC_ABIs_DIR + "WETH-ABI.json", log["address"].lower(), idx, "Transfer")
                        self.store_erc20_fact(transaction, SOURCE_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["src"].lower(), decodedEvent["dst"].lower(), decodedEvent["wad"])

                elif log["address"].lower() == SOURCE_CHAIN_BRIDGE_ADDRESS_V2 and additional_data:
                    
                    # Withdrew(bytes32,tuple)
                    if log["topics"][0].hex().startswith("21e88e"):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_v2_event_data(transaction, SC_ABIs_DIR + "RONIN-BRIDGE-CONTRACT-V2.json", log["address"].lower(), idx)
                        receipt = decodedEvent["receipt"]

                        if receipt['info']['erc'] == 1: # since this will only occur within the additional data, we will ignore NFTs, because there are not NFT transfers in the selected interval
                            return
                        
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, receipt['id'], receipt['mainchain']["addr"].lower(), receipt['mainchain']['tokenAddr'].lower(), receipt['info']["quantity"]))

                        if receipt['mainchain']['tokenAddr'].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN:
                            deals_with_native_tokens = True

                else: # there is the transfer of another token
                    # Transfer(address,address,uint256)
                    if log["topics"][0].hex().startswith("ddf252"): # there is the transfer of a token
                        try:
                            decodedEvent = self.sc_transactionDecoder.decode_erc20_event_data(transaction, ABIs_DIR + "ERC20-ABI.json", log["address"].lower(), idx)

                            self.store_erc20_fact(transaction, SOURCE_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                        except Exception as e:
                            pass # we ignore as this is a token not mapped
                    else:
                        # we can just ignore as this is an Approval, or e.g., VoterVotesChanged in Frax Finance: FXS Token
                        pass

            tx_value = 0
            # we want to extract the eth being transferred to the bridge if this is a transfer of native tokens through the bridge
            # or, transfers made directly to the bridge that do not emit events (just for stats)
            if deals_with_native_tokens or (not transaction["logs"] and convert_hex_to_int(transaction["status"])) or (len(transaction["logs"]) == 1 and transaction["logs"][0]["address"] == SOURCE_CHAIN_BRIDGE_ADDRESS_V2):
                # if we are dealing with native tokens we need to get the transaction value
                tx_value = self.sc_transactionDecoder.get_transaction(transaction["transactionHash"])["value"]

                if tx_value == 0 and deals_with_native_tokens:
                    tx_value = self.sc_transactionDecoder.debug_transaction_trace(transaction["transactionHash"])

            self.store_transaction_fact(blocks, SOURCE_CHAIN_ID, transaction, tx_value, transaction_facts)

        except Exception as e:
            errors.write("RoninFactsExtractor: %s\t%s\n" % (transaction["transactionHash"], e))

    def tc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        additional_data = False

        if only_deposits or only_withdrawals:
            additional_data = True

        transaction_facts, erc20_transfer_facts, _, token_deposited_facts, token_withdrew_facts, _, errors = output_files

        #print("Extracting facts (Target Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        # this map allows us to keep track of the index of the event (not within the whole transaction, but emitted by contract interface)
        # this is necessary for decoding the logs of the transaction, and then knowing what is the current log based on the current index

        try:
            for idx, log in enumerate(transaction["logs"]):
                convert_topics_to_hex(log)
                if log["address"] == TARGET_CHAIN_BRIDGE_ADDRESS:

                    # TokenWithdrew(uint256,address,address,address,uint32,uint256)
                    if log["topics"][0].hex().startswith("d56c021e") and (only_withdrawals or not additional_data):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction, TC_ABIs_DIR + "BRIDGE-ABI.json", log["address"].lower(), idx, "Withdrawal")
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent['_withdrawId'], decodedEvent['_owner'].lower(), decodedEvent['_tokenAddress'].lower(), decodedEvent['_mainchainAddress'].lower(), SOURCE_CHAIN_ID, decodedEvent['_standard'], decodedEvent['_tokenNumber']))

                    # TokenDeposited(uint256,address,address,uint256)
                    if log["topics"][0].hex().startswith("5187d31a") and (only_deposits or not additional_data):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction, TC_ABIs_DIR + "BRIDGE-ABI.json", log["address"].lower(), idx, "Deposit")
                        token_deposited_facts.write("%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, decodedEvent["depositId"], decodedEvent['owner'].lower(), decodedEvent["tokenAddress"].lower(), decodedEvent['tokenNumber']))

                else: # there is the transfer of a token
                    # Transfer(address,address,uint256)
                    if log["topics"][0].hex().startswith("ddf252"):
                        decodedEvent = self.tc_transactionDecoder.decode_erc20_event_data(transaction, ABIs_DIR + "ERC20-ABI.json", log["address"].lower(), idx)
                        self.store_erc20_fact(transaction, TARGET_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                        idx += 1
                    else:
                        # we can just ignore as this is another contract or an Approval event
                        pass

            self.store_transaction_fact(blocks, TARGET_CHAIN_ID, transaction, 0, transaction_facts) # In Ronin, the tx value is always 0

        except Exception as e:
            errors.write("RoninFactsExtractor: %s\t%s\n" % (transaction["transactionHash"], e))
