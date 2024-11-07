from utils.NomadTransactionDataDecoder import NomadTransactionDataDecoder
from utils.utils import convert_hex_to_int, convert_topics_to_hex, get_token_mapping
from FactsExtractor import FactsExtractor
from utils.nomad_env import (
    CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
    CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN,
    SOURCE_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE,
    TARGET_CHAIN_ABI_HOME_CONTRACT,
    TARGET_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE,
    TARGET_CHAIN_CONNECTION_URL,
    TARGET_CHAIN_CONNECTION_OPTIONS,
    TARGET_CHAIN_BRIDGE_ADDRESS_WITHDRAWALS,
    SOURCE_CHAIN_BRIDGE_ADDRESS_DEPOSITS,
    SOURCE_CHAIN_ID,
    SOURCE_CHAIN_ID,
    TARGET_CHAIN_ID,
    SOURCE_CHAIN_CONNECTION_URL,
    SOURCE_CHAIN_CONNECTION_OPTIONS,
    TOKEN_MAPPINGS,
    SOURCE_CHAIN_ABI_HOME_CONTRACT,
    ABIs_DIR,
    SC_ABIs_DIR,
    TC_ABIs_DIR,
)

class NomadFactsExtractor(FactsExtractor):

    def __init__(self, facts_folder, evaluation_folder):
        super().__init__(facts_folder, evaluation_folder)
        self.sc_transactionDecoder = NomadTransactionDataDecoder(SOURCE_CHAIN_CONNECTION_URL, SOURCE_CHAIN_CONNECTION_OPTIONS)
        self.tc_transactionDecoder = NomadTransactionDataDecoder(TARGET_CHAIN_CONNECTION_URL, TARGET_CHAIN_CONNECTION_OPTIONS)

    def sc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        deals_with_native_tokens = False
        additional_data = False

        if only_deposits or only_withdrawals:
            additional_data = True

        transaction_facts, erc20_transfer_facts, deposit_facts, _, token_deposited_facts, token_withdrew_facts, alternative_chains_facts, errors = output_files
        
        # print("Extracting facts (Source Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        nonce = None
        try:
            function, dst_chain = self.extract_dst_chain_from_tx_input_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS.json", SOURCE_CHAIN_BRIDGE_ADDRESS_DEPOSITS, SOURCE_CHAIN_ID)
            function_2, dst_chain_2 = self.extract_dst_chain_from_tx_input_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", SOURCE_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE, SOURCE_CHAIN_ID)

            if dst_chain != None: dst_chain = dst_chain["_destination"]
            if dst_chain_2 != None: dst_chain_2 = dst_chain_2["_domain"]

            # ignore cross-chain transactions that are not targeted to the blockchains in analysis
            if dst_chain != TARGET_CHAIN_ID and dst_chain_2 != TARGET_CHAIN_ID:
                if dst_chain != None:
                    # transaction targeted to another blockchain
                    alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (SOURCE_CHAIN_ID, transaction["transactionHash"], dst_chain, transaction["from"], transaction["to"], function))
                    return
                elif dst_chain_2 != None:
                    # transaction targeted to another blockchain
                    alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (SOURCE_CHAIN_ID, transaction["transactionHash"], dst_chain_2, transaction["from"], transaction["to"], function_2))
                    return

                # if dst_chain == None or dst_chain_2 == None, the transaction is not a deposit
                # it is either calling the withdrawal contract, or may be a tx that reverted
            
            for idx, log in enumerate(transaction["logs"]):
                convert_topics_to_hex(log)
                if log["address"] == SOURCE_CHAIN_BRIDGE_ADDRESS_DEPOSITS:
                    # Send(address,address,uint32,bytes32,uint256,bool)
                    if log["topics"][0].hex().startswith("a3d219") and (only_deposits or not additional_data):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS.json", log["address"].lower(), idx, "Deposit")
                        if decodedEvent['toDomain'] != TARGET_CHAIN_ID:
                            alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (SOURCE_CHAIN_ID, transaction["transactionHash"], decodedEvent['toDomain'], transaction["from"], transaction["to"], None))
                            return
                        token_deposited_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, nonce, self.extract_hex_value(decodedEvent['toId'].hex()), get_token_mapping(2, 3, decodedEvent["token"].lower(), TOKEN_MAPPINGS), decodedEvent["token"].lower(), decodedEvent['toDomain'], 20, decodedEvent['amount']))

                    # Receive(uint64,address,address,address,uint256)
                    elif log["topics"][0].hex().startswith("9f9a97") and (only_withdrawals or not additional_data):
                        decodedEvent = self.sc_transactionDecoder.decode_bridge_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS.json", log["address"].lower(), idx, "Withdrawal")
                        origin, nonce = self.extract_destination_and_nonce(decodedEvent["originAndNonce"])

                        if origin == TARGET_CHAIN_ID:
                            token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, nonce, decodedEvent['recipient'].lower(), decodedEvent['token'].lower(), decodedEvent['amount']))
                        else:
                            alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (SOURCE_CHAIN_ID, transaction["transactionHash"], origin, transaction["from"], transaction["to"], None))
                            return

                elif log["address"] == SOURCE_CHAIN_ABI_HOME_CONTRACT:
                    # Dispatch(bytes32,uint256,uint64,bytes32,bytes)
                    if log["topics"][0].hex().startswith("9d4c83"):
                        decodedEvent = self.sc_transactionDecoder.decode_home_contract_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-HOME.json", log["address"].lower(), idx)
                        _, nonce = self.extract_destination_and_nonce(decodedEvent["destinationAndNonce"])

                elif log["address"] == "0x049b51e531fd8f90da6d92ea83dc4125002f20ef" or log["address"] == "0x5d94309e5a0090b165fa4181519701637b6daeba": # The "Process" event is irrelevant
                    pass

                elif log["address"].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN:

                    # Deposit(address,uint256)
                    if log["topics"][0].hex().startswith("e1fffc"):
                        deals_with_native_tokens = True
                        decodedEvent, _ = self.sc_transactionDecoder.decode_weth_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", SC_ABIs_DIR + "WETH-ABI.json", log["address"].lower(), idx, "Deposit")
                        deposit_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, transaction["from"], decodedEvent["dst"].lower(), decodedEvent["wad"]))

                    # Transfer(address,address,uint256)
                    elif log["topics"][0].hex().startswith("ddf252") and not deals_with_native_tokens and not additional_data: # there is the transfer of a token
                        decodedEvent, _ = self.sc_transactionDecoder.decode_weth_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", SC_ABIs_DIR + "WETH-ABI.json", log["address"].lower(), idx, "Transfer")
                        self.store_erc20_fact(transaction, SOURCE_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["src"].lower(), decodedEvent["dst"].lower(), decodedEvent["wad"])

                else: # log emitted by some token
                    if deals_with_native_tokens == True:
                        # if we are dealing with native tokens, ignore Transfer event, because the Deposit() event was already captured
                        pass

                    # Transfer(address,address,uint256)
                    if log["topics"][0].hex().startswith("ddf252") and not additional_data: # there is the transfer of a token
                        decodedEvent = self.sc_transactionDecoder.decode_erc20_event_data(transaction, ABIs_DIR + "ERC20-ABI.json", log["address"].lower(), idx)
                        self.store_erc20_fact(transaction, SOURCE_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                    else:
                        # we can just ignore as this is an Approval, or e.g., VoterVotesChanged in Frax Finance: FXS Token
                        pass

            tx_value = 0
            # we want to extract the eth being transferred to the bridge if this is a transfer of native tokens through the bridge
            # or, transfers made directly to the bridge that do not emit events (just for stats)
            if deals_with_native_tokens or (not transaction["logs"] and convert_hex_to_int(transaction["status"])):
                # if we are dealing with native tokens we need to get the transaction value
                tx_value = self.sc_transactionDecoder.get_transaction(transaction["transactionHash"])["value"]

                if tx_value == 0 and deals_with_native_tokens:
                    # this may be a request done by another protocol and the main tx does not carry any value
                    # we need to then retrieve the value from an internal tx
                    tx_value = self.sc_transactionDecoder.debug_transaction_trace(transaction["transactionHash"])

            self.store_transaction_fact(blocks, SOURCE_CHAIN_ID, transaction, tx_value, transaction_facts)

        except Exception as e:
            errors.write("NomadFactsExtractor: %s\t%s\n" % (transaction["transactionHash"], e))

    def tc_extract_facts_from_transaction(self, transaction, blocks, output_files, only_deposits, only_withdrawals):
        deals_with_native_tokens = False

        transaction_facts, erc20_transfer_facts, withdrawal_facts, token_deposited_facts, token_withdrew_facts, alternative_chains_facts, errors = output_files

        # print("Extracting facts (Target Chain). Transaction: " + transaction["transactionHash"] + " | Block: " + str(convert_hex_to_int(transaction["blockNumber"])))

        nonce = None
        try:
            function, dst_chain = self.extract_dst_chain_from_tx_input_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-WITHDRAWALS.json", TARGET_CHAIN_BRIDGE_ADDRESS_WITHDRAWALS, TARGET_CHAIN_ID)
            function_2, dst_chain_2 = self.extract_dst_chain_from_tx_input_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", TARGET_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE, TARGET_CHAIN_ID)

            if dst_chain != None: dst_chain = dst_chain["_destination"]
            if dst_chain_2 != None: dst_chain_2 = dst_chain_2["_domain"]

            # ignore cross-chain transactions that are not targeted to the blockchains in analysis
            if dst_chain != SOURCE_CHAIN_ID and dst_chain_2 != SOURCE_CHAIN_ID:
                if dst_chain != None:
                    # transaction targeted to another blockchain
                    alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (TARGET_CHAIN_ID, transaction["transactionHash"], dst_chain, transaction["from"], transaction["to"], function))
                    return
                
                elif dst_chain_2 != None:
                    alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (TARGET_CHAIN_ID, transaction["transactionHash"], dst_chain_2, transaction["from"], transaction["to"], function_2))
                    return

                # if dst_chain == None, the transaction is not a deposit
                # it is either calling the withdrawal contract, or may be a tx that reverted
            
            for idx, log in enumerate(transaction["logs"]):
                convert_topics_to_hex(log)
                if log["address"] == TARGET_CHAIN_BRIDGE_ADDRESS_WITHDRAWALS:
                    # Send(address,address,uint32,bytes32,uint256,bool)
                    if log["topics"][0].hex().startswith("a3d219"):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-WITHDRAWALS.json", log["address"].lower(), idx, "Deposit")
                        token_withdrew_facts.write("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, nonce, self.extract_hex_value(decodedEvent['toId'].hex()), decodedEvent['token'].lower(), get_token_mapping(3, 2, decodedEvent['token'].lower(), TOKEN_MAPPINGS), SOURCE_CHAIN_ID, 20, decodedEvent['amount']))

                    # Receive(uint64,address,address,address,uint256)
                    elif log["topics"][0].hex().startswith("9f9a97"):
                        decodedEvent = self.tc_transactionDecoder.decode_bridge_event_data(transaction, SC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS.json", log["address"].lower(), idx, "Withdrawal")
                        origin_chain_id, nonce = self.extract_destination_and_nonce(decodedEvent["originAndNonce"])

                        if origin_chain_id == SOURCE_CHAIN_ID:
                            token_deposited_facts.write("%s\t%d\t%s\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, nonce, decodedEvent['recipient'].lower(), decodedEvent["token"].lower(), decodedEvent["amount"]))
                        else:
                            alternative_chains_facts.write("%d\t%s\t%d\t%s\t%s\t%s\r\n" % (TARGET_CHAIN_ID, transaction["transactionHash"], origin_chain_id, transaction["from"], transaction["to"], None))
                            return
                            


                elif log["address"] == TARGET_CHAIN_ABI_HOME_CONTRACT:
                    # Dispatch(bytes32,uint256,uint64,bytes32,bytes)
                    if log["topics"][0].hex().startswith("9d4c83"):
                        decodedEvent = self.tc_transactionDecoder.decode_home_contract_event_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-HOME.json", log["address"].lower(), idx)
                        _, nonce = self.extract_destination_and_nonce(decodedEvent["destinationAndNonce"])


                elif log["address"] == "0x7f58bb8311db968ab110889f2dfa04ab7e8e831b" or log["address"] == TARGET_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE: # Process event irrelevant
                    pass

                elif log["address"].lower() == CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN:

                    # Deposit(address,uint256)
                    if log["topics"][0].hex().startswith("e1fffc"):
                        deals_with_native_tokens = True
                        decodedEvent, _ = self.tc_transactionDecoder.decode_weth_event_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", TC_ABIs_DIR + "WGLMR-ABI.json", log["address"].lower(), idx, "Deposit")
                        withdrawal_facts.write("%s\t%d\t%s\t%s\t%s\r\n" % (transaction["transactionHash"], idx, transaction["from"], decodedEvent["dst"].lower(), decodedEvent["wad"]))

                    # Transfer(address,address,uint256)
                    elif log["topics"][0].hex().startswith("ddf252") and not deals_with_native_tokens:
                        decodedEvent, _ = self.tc_transactionDecoder.decode_weth_event_data(transaction, TC_ABIs_DIR + "NOMAD-BRIDGE-DEPOSITS-NATIVE.json", TC_ABIs_DIR + "WGLMR-ABI.json", log["address"].lower(), idx, "Transfer")
                        self.store_erc20_fact(transaction, TARGET_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["src"].lower(), decodedEvent["dst"].lower(), decodedEvent["wad"])

                else: # log emitted by some token
                    if deals_with_native_tokens == True:
                        # if we are dealing with native tokens, ignore Transfer event, because the Deposit() event was already captured
                        pass

                    # Transfer(address,address,uint256)
                    if log["topics"][0].hex().startswith("ddf252"): # there is the transfer of a token
                        decodedEvent = self.tc_transactionDecoder.decode_erc20_event_data(transaction, ABIs_DIR + "ERC20-ABI.json", log["address"].lower(), idx)
                        self.store_erc20_fact(transaction, TARGET_CHAIN_ID, idx, log, erc20_transfer_facts, decodedEvent["from"].lower(), decodedEvent["to"].lower(), decodedEvent["value"])
                    else:
                        # we can just ignore as this is an Approval, or e.g., VoterVotesChanged in Frax Finance: FXS Token
                        pass

            tx_value = 0
            # we want to extract the eth being transferred to the bridge if this is a transfer of native tokens through the bridge
            # or, transfers made directly to the bridge that do not emit events (just for stats)
            if deals_with_native_tokens or (not transaction["logs"] and convert_hex_to_int(transaction["status"])):
                # if we are dealing with native tokens we need to get the transaction value
                tx_value = self.tc_transactionDecoder.get_transaction(transaction["transactionHash"])["value"]

            self.store_transaction_fact(blocks, TARGET_CHAIN_ID, transaction, tx_value, transaction_facts)

        except Exception as e:
            errors.write("NomadFactsExtractor: %s\t%s\n" % (transaction["transactionHash"], e))

    def extract_destination_and_nonce(self, combined):
        destination = (combined >> 32) & 0xFFFFFFFF
        nonce = combined & 0xFFFFFFFF
        return destination, nonce

    def extract_hex_value(self, input_str):
        # turn something like 33333331D5205CC38E34A1C245DF69985B9E5BE5000000000000000000000000 or 0000000000000000000000000000000B4D325BB539676DAC6EC3413D5974CF0F
        # into 0x33333331d5205cc38e34a1c245df69985b9e5be5 and 0x0000000b4d325bb539676dac6ec3413d5974cf0f
        if len(input_str) != 64:
            raise ValueError("Input string must be exactly 64 characters long")

        if input_str.startswith('0' * 24):
            return '0x' + input_str[24:].lower()

        if input_str.endswith('0' * 24):
            return '0x' + input_str[:-24].lower()

        raise ValueError("Input string does not contain 24 zeros at the start or the end")


    def extract_dst_chain_from_tx_input_data(self, transaction, contract_abi, contract_address, chain_id):
        tx_hash = transaction["transactionHash"]

        if transaction["to"] == contract_address and transaction["logs"] != []:
            req_data = None
            if chain_id == SOURCE_CHAIN_ID:
                req_data = self.sc_transactionDecoder.decode_transaction_data(contract_abi, self.sc_transactionDecoder.get_transaction(tx_hash)["input"], contract_address)
            elif chain_id == TARGET_CHAIN_ID:
                req_data = self.tc_transactionDecoder.decode_transaction_data(contract_abi, self.tc_transactionDecoder.get_transaction(tx_hash)["input"], contract_address)
            else:
                raise Exception("NomadFactsExtractor: Invalid chain id to choose tx decoder")

            return req_data[0], req_data[1] # we extract the dst_chain from the user request
        else:
            return None, None # then this request is not a Deposit ("Send") request or a tx that reverted
