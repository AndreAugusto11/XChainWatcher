from utils import ronin_env
from utils import nomad_env
from NomadFactsExtractor import NomadFactsExtractor
from RoninFactsExtractor import RoninFactsExtractor
from BridgeFactsExtractor import BridgeFactsExtractor
from utils.utils import load_transaction_receipts, extract_block_data_to_dict
import concurrent.futures
import sys


def process_ronin_bridge_facts():
    bridge_facts_extractor = BridgeFactsExtractor(ronin_env.FACTS_FOLDER)
    bridge_facts_extractor.extract_facts_from_bridge(
        ronin_env.TOKEN_MAPPINGS,
        ronin_env.BRIDGE_CONTROLLED_ADDRESSES,
        ronin_env.SOURCE_CHAIN_ID,
        ronin_env.TARGET_CHAIN_ID,
        ronin_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
        ronin_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN,
    )


def process_nomad_bridge_facts():
    bridge_facts_extractor = BridgeFactsExtractor(nomad_env.FACTS_FOLDER)
    bridge_facts_extractor.extract_facts_from_bridge(
        nomad_env.TOKEN_MAPPINGS,
        nomad_env.BRIDGE_CONTROLLED_ADDRESSES,
        nomad_env.SOURCE_CHAIN_ID,
        nomad_env.TARGET_CHAIN_ID,
        nomad_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
        nomad_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN,
    )


def process_chunk(
    thread_info,
    facts_extractor,
    chain_id,
    chunk,
    transactions,
    blocks,
    only_deposits,
    only_withdrawals,
):
    PREFIX_FILENAME = ""
    if only_deposits or only_withdrawals:
        PREFIX_FILENAME = "additional_"

    tid, start_idx, end_idx = thread_info
        
    if chain_id == ronin_env.SOURCE_CHAIN_ID or chain_id == nomad_env.SOURCE_CHAIN_ID:
        transaction_facts          = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "transaction.facts",        "a")
        erc20_transfer_facts       = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "erc20_transfer.facts",     "a")
        deposit_facts              = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "sc_deposit.facts",         "a")
        token_deposited_facts      = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "sc_token_deposited.facts", "a")
        token_withdrew_facts       = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "sc_token_withdrew.facts",  "a")
        alternative_chains_facts   = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "alternative_chains.facts", "a")
        errors                     = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "sc_errors.txt",            "a")

        for index in chunk:
            if index % 10 == 0:
                print(f"{tid}: {index}/{chunk} {(index-start_idx)/(end_idx-start_idx)*100}%")

            facts_extractor.sc_extract_facts_from_transaction(
                transactions[index],
                blocks,
                [
                    transaction_facts,
                    erc20_transfer_facts,
                    deposit_facts,
                    withdrawal_facts,
                    token_deposited_facts,
                    token_withdrew_facts,
                    alternative_chains_facts,
                    errors
                ],
                only_deposits,
                only_withdrawals
            )

    elif chain_id == ronin_env.TARGET_CHAIN_ID or chain_id == nomad_env.TARGET_CHAIN_ID:
        transaction_facts          = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "transaction.facts",        "a")
        erc20_transfer_facts       = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "erc20_transfer.facts",     "a")
        withdrawal_facts           = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "tc_withdrawal.facts",      "a")
        token_deposited_facts      = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "tc_token_deposited.facts", "a")
        token_withdrew_facts       = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "tc_token_withdrew.facts",  "a")
        alternative_chains_facts   = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "alternative_chains.facts", "a")
        errors                     = open(facts_extractor.facts_folder + "/" + PREFIX_FILENAME + "tc_errors.txt",            "a")

        for index in chunk:
            if index % 100 == 0:
                print(f"{tid}: {index}/{chunk} {(index-start_idx)/(end_idx-start_idx)*100}%")

            facts_extractor.tc_extract_facts_from_transaction(
                transactions[index],
                blocks,
                [
                    transaction_facts,
                    erc20_transfer_facts,
                    deposit_facts,
                    withdrawal_facts,
                    token_deposited_facts,
                    token_withdrew_facts,
                    alternative_chains_facts,
                    errors
                ],
                only_deposits,
                only_withdrawals
            )

    else:
        print("Invalid chain id provided... Closing...")
        return

    transaction_facts.close()
    erc20_transfer_facts.close()
    deposit_facts.close()
    withdrawal_facts.close()
    token_deposited_facts.close()
    token_withdrew_facts.close()
    alternative_chains_facts.close()
    errors.close()

def process_transactions(
    facts_extractor, env_file, chain_id, transactions, blocks, only_deposits, only_withdrawals
):
    max_num_threads = env_file.MAX_NUM_THREADS_SOURCE_CHAIN if chain_id == env_file.SOURCE_CHAIN_ID else env_file.MAX_NUM_THREADS_TARGET_CHAIN

    start = 0
    end = len(transactions)
    interval_range = range(start, end + 1)
    chunk_size = len(interval_range) // max_num_threads + 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_num_threads) as executor:
        start_idx = 0
        futures = []
        for tid in range(max_num_threads):
            end_idx = start_idx + min(chunk_size, end - start_idx)
            chunk = interval_range[start_idx:end_idx]
            futures.append(
                executor.submit(
                    process_chunk,
                    (tid, start_idx, end_idx),
                    facts_extractor,
                    chain_id,
                    chunk,
                    transactions,
                    blocks,
                    only_deposits,
                    only_withdrawals,
                )
            )
            start_idx = end_idx

        # Wait for all threads to finish before moving on to the next interval
        for future in futures:
            future.result()


def process_ronin_bridge():
    process_ronin_bridge_facts()

    # Create a Transaction Facts Extractor for the Ronin Bridge
    ronin_bridge_facts_extractor = RoninFactsExtractor(
        ronin_env.FACTS_FOLDER
    )

    # Load Source Chain Blocks and Tx Receipts
    blocks = extract_block_data_to_dict(ronin_env.FILENAME_SOURCE_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        ronin_env.FILENAME_SOURCE_CHAIN_TRANSACTION_RECEIPTS
    )

    print("Processing Ethereum transactions...")
    process_transactions(
        ronin_bridge_facts_extractor,
        ronin_env,
        ronin_env.SOURCE_CHAIN_ID,
        transactions,
        blocks,
        False,
        False,
    )

    # Load Target Chain Blocks and Tx Receipts
    blocks = extract_block_data_to_dict(ronin_env.FILENAME_TARGET_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        ronin_env.FILENAME_TARGET_CHAIN_TRANSACTION_RECEIPTS
    )

    print("Processing Ronin transactions...")
    process_transactions(
        ronin_bridge_facts_extractor,
        ronin_env,
        ronin_env.TARGET_CHAIN_ID,
        transactions,
        blocks,
        False,
        False,
    )

    # Load Additional Blocks and Tx Receipts from the Source Chain After Interval
    blocks = extract_block_data_to_dict(ronin_env.FILENAME_SOURCE_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        ronin_env.FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS_AFTER
    )

    print("Processing Ethereum additional transactions...")
    process_transactions(
        ronin_bridge_facts_extractor,
        ronin_env,
        ronin_env.SOURCE_CHAIN_ID,
        transactions,
        blocks,
        False,
        True,
    )

    # Load Additional Blocks and Tx Receipts from the Source Chain Before Interval
    blocks = extract_block_data_to_dict(ronin_env.FILENAME_SOURCE_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        ronin_env.FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS_BEFORE
    )

    print("Processing Ethereum additional transactions...")
    process_transactions(
        ronin_bridge_facts_extractor,
        ronin_env,
        ronin_env.SOURCE_CHAIN_ID,
        transactions,
        blocks,
        True,
        False,
    )

    # Load Additional Blocks and Tx Receipts from the Target Chain
    blocks = extract_block_data_to_dict(ronin_env.FILENAME_TARGET_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        ronin_env.FILENAME_TARGET_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS
    )

    print("Processing Ronin additional transactions...")
    process_transactions(
        ronin_bridge_facts_extractor,
        ronin_env,
        ronin_env.TARGET_CHAIN_ID,
        transactions,
        blocks,
        False,
        True,
    )


def process_nomad_bridge():
    process_nomad_bridge_facts()

    ## Create a Transaction Facts Extractor for the Nomad Bridge
    nomad_bridge_facts_extractor = NomadFactsExtractor(
        nomad_env.FACTS_FOLDER
    )

    blocks = extract_block_data_to_dict(nomad_env.FILENAME_SOURCE_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        nomad_env.FILENAME_SOURCE_CHAIN_TRANSACTION_RECEIPTS
    )

    print("Processing Ethereum transactions...")
    process_transactions(nomad_bridge_facts_extractor, nomad_env, nomad_env.SOURCE_CHAIN_ID, transactions, blocks, False, False)

    # process target chain transactions
    blocks = extract_block_data_to_dict(nomad_env.FILENAME_TARGET_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        nomad_env.FILENAME_TARGET_CHAIN_TRANSACTION_RECEIPTS
    )

    print("Processing Moonbeam transactions...")
    process_transactions(nomad_bridge_facts_extractor, nomad_env, nomad_env.TARGET_CHAIN_ID, transactions, blocks, False, False)

    # Load Additional Blocks and Tx Receipts from the Source Chain
    blocks = extract_block_data_to_dict(nomad_env.FILENAME_SOURCE_CHAIN_BLOCK_DATA)
    transactions = load_transaction_receipts(
        nomad_env.FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS
    )

    print("Processing Ethereum additional transactions...")
    process_transactions(nomad_bridge_facts_extractor, nomad_env, nomad_env.SOURCE_CHAIN_ID, transactions, blocks, False, True)

def usage():
    print("Usage:")
    print("python main.py <bridge_name>")
    print("")
    print("Bridges currently supported: ronin | nomad")


def main():

    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] not in ["ronin", "nomad"]:
        print("Bridge not supported")

    match sys.argv[1]:
        case "ronin":
            process_ronin_bridge()
        case "nomad":
            process_nomad_bridge()


if __name__ == "__main__":
    main()
