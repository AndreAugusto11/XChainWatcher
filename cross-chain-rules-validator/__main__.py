from utils import ronin_env
from utils import nomad_env
from NomadFactsExtractor import NomadFactsExtractor
from RoninFactsExtractor import RoninFactsExtractor
from BridgeFactsExtractor import BridgeFactsExtractor
from utils.utils import load_transaction_receipts, extract_block_data_to_dict, confirm_api_keys_loaded
from queue import Queue
import threading
import time
import sys
import os

global processed_count
global total_receipts

def process_ronin_bridge_facts():
    bridge_facts_extractor = BridgeFactsExtractor(
        ronin_env.FACTS_FOLDER,
    )

    bridge_facts_extractor.extract_facts_from_bridge(
        ronin_env.TOKEN_MAPPINGS,
        ronin_env.BRIDGE_CONTROLLED_ADDRESSES,
        ronin_env.SOURCE_CHAIN_ID,
        ronin_env.TARGET_CHAIN_ID,
        ronin_env.SOURCE_CHAIN_FINALITY_TIME,
        ronin_env.TARGET_CHAIN_FINALITY_TIME,
        ronin_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
        ronin_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN,
    )


def process_nomad_bridge_facts():
    bridge_facts_extractor = BridgeFactsExtractor(
        nomad_env.FACTS_FOLDER,
    )
    bridge_facts_extractor.extract_facts_from_bridge(
        nomad_env.TOKEN_MAPPINGS,
        nomad_env.BRIDGE_CONTROLLED_ADDRESSES,
        nomad_env.SOURCE_CHAIN_ID,
        nomad_env.TARGET_CHAIN_ID,
        nomad_env.SOURCE_CHAIN_FINALITY_TIME,
        nomad_env.TARGET_CHAIN_FINALITY_TIME,
        nomad_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN,
        nomad_env.CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN,
    )

def process_chunk(
    facts_extractor,
    chain_id,
    chunk,
    blocks,
    only_deposits,
    only_withdrawals,
):
    global processed_count
    global total_receipts
    thread_name = threading.current_thread().name

    PREFIX_FILENAME = ""
    if only_deposits or only_withdrawals:
        PREFIX_FILENAME = "additional_"
        
    if chain_id == ronin_env.SOURCE_CHAIN_ID or chain_id == nomad_env.SOURCE_CHAIN_ID:
        transaction_facts          = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "transaction.facts",        "a")
        erc20_transfer_facts       = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "erc20_transfer.facts",     "a")
        deposit_facts              = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "sc_deposit.facts",         "a")
        withdrawal_facts           = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "sc_withdrawal.facts",      "a")
        token_deposited_facts      = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "sc_token_deposited.facts", "a")
        token_withdrew_facts       = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "sc_token_withdrew.facts",  "a")
        alternative_chains_facts   = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "alternative_chains.facts", "a")
        errors                     = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "sc_errors.txt",            "a")
        evaluation                 = open(facts_extractor.evaluation_folder + thread_name + "_" +                   "evaluation.csv",           "a")

        for transaction in chunk:
            start_time = time.time()
            facts_extractor.sc_extract_facts_from_transaction(
                transaction,
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
            
            execution_time = time.time() - start_time
            evaluation.write(f"{transaction['transactionHash']},{len(transaction['logs'])},{execution_time}\n")

    elif chain_id == ronin_env.TARGET_CHAIN_ID or chain_id == nomad_env.TARGET_CHAIN_ID:
        transaction_facts          = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "transaction.facts",        "a")
        erc20_transfer_facts       = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "erc20_transfer.facts",     "a")
        withdrawal_facts           = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "tc_withdrawal.facts",      "a")
        token_deposited_facts      = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "tc_token_deposited.facts", "a")
        token_withdrew_facts       = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "tc_token_withdrew.facts",  "a")
        alternative_chains_facts   = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "alternative_chains.facts", "a")
        errors                     = open(facts_extractor.facts_folder      + thread_name + "_" + PREFIX_FILENAME + "tc_errors.txt",            "a")
        evaluation                 = open(facts_extractor.evaluation_folder + thread_name + "_" +                   "evaluation.csv",           "a")

        for transaction in chunk:
            start_time = time.time()
            facts_extractor.tc_extract_facts_from_transaction(
                transaction,
                blocks,
                [
                    transaction_facts,
                    erc20_transfer_facts,
                    withdrawal_facts,
                    token_deposited_facts,
                    token_withdrew_facts,
                    alternative_chains_facts,
                    errors
                ],
                only_deposits,
                only_withdrawals
            )
            
            execution_time = time.time() - start_time
            evaluation.write(f"{transaction['transactionHash']},{len(transaction['logs'])},{execution_time}\n")

    else:
        print("Invalid chain id provided... Closing...")
        return

    transaction_facts.close()
    erc20_transfer_facts.close()
    token_deposited_facts.close()
    token_withdrew_facts.close()
    alternative_chains_facts.close()
    errors.close()
    withdrawal_facts.close()
    evaluation.close()

    with lock:
        processed_count += len(chunk)
        if processed_count > total_receipts:
            processed_count = total_receipts
        percentage = (processed_count / total_receipts) * 100
        print(f"Global progress: {percentage:.2f}%")

    if chain_id == ronin_env.SOURCE_CHAIN_ID or chain_id == nomad_env.SOURCE_CHAIN_ID:
        deposit_facts.close()


lock = threading.Lock()

def worker(queue, facts_extractor, chain_id, transactions, blocks, only_deposits, only_withdrawals):
    while True:
        chunk = queue.get()
        if chunk is None:
            break
        process_chunk(facts_extractor, chain_id, chunk, blocks, only_deposits, only_withdrawals)
        queue.task_done()


def process_transactions(
    facts_extractor, env_file, chain_id, transactions, blocks, only_deposits, only_withdrawals
):
    # Shared variable to track the number of processed receipts
    global processed_count
    global total_receipts
    
    processed_count = 0
    total_receipts = len(transactions)

    max_num_threads = env_file.MAX_NUM_THREADS_SOURCE_CHAIN if chain_id == env_file.SOURCE_CHAIN_ID else env_file.MAX_NUM_THREADS_TARGET_CHAIN

    # a queue to hold chunks of 500 receipts
    queue = Queue()

    threads = []
    for i in range(max_num_threads):
        t = threading.Thread(
            target=worker, args=(
                queue,
                facts_extractor,
                chain_id,
                transactions,
                blocks,
                only_deposits,
                only_withdrawals
            ),
            name=f"Thread-{i+1}"
        )
        t.start()
        threads.append(t)

    for i in range(0, total_receipts, 500):
        queue.put(transactions[i:i + 500])

    queue.join()

    for _ in range(max_num_threads):
        queue.put(None)

    for t in threads:
        t.join()


def process_ronin_bridge():
    process_ronin_bridge_facts()

    # Create a Transaction Facts Extractor for the Ronin Bridge
    ronin_bridge_facts_extractor = RoninFactsExtractor(
        ronin_env.FACTS_FOLDER,
        ronin_env.EVALUATION_FOLDER,
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

    merge_threads_files(ronin_env)


def process_nomad_bridge():
    process_nomad_bridge_facts()

    ## Create a Transaction Facts Extractor for the Nomad Bridge
    nomad_bridge_facts_extractor = NomadFactsExtractor(
        nomad_env.FACTS_FOLDER,
        nomad_env.EVALUATION_FOLDER,
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

    merge_threads_files(nomad_env)


def merge_threads_files(env_file):
    threads_files = [
        "transaction.facts",
        "erc20_transfer.facts",
        "sc_deposit.facts",
        "sc_withdrawal.facts",
        "sc_token_deposited.facts",
        "sc_token_withdrew.facts",
        "alternative_chains.facts",
        "sc_errors.txt",
        "tc_withdrawal.facts",
        "tc_token_deposited.facts",
        "tc_token_withdrew.facts",
        "tc_errors.txt",
    ]

    max_num_threads = env_file.MAX_NUM_THREADS_SOURCE_CHAIN if env_file.MAX_NUM_THREADS_SOURCE_CHAIN > env_file.MAX_NUM_THREADS_TARGET_CHAIN else env_file.MAX_NUM_THREADS_TARGET_CHAIN

    for file in threads_files:
        with open(env_file.FACTS_FOLDER + file, "w") as outfile:
            for thread in range(1, max_num_threads + 1):
                try:
                    with open(env_file.FACTS_FOLDER + "Thread-" + str(thread) + "_" + file) as infile:
                        outfile.write(infile.read())
                    
                    os.remove(env_file.FACTS_FOLDER + "Thread-" + str(thread) + "_" + file)

                except FileNotFoundError:
                    pass

    for file in threads_files:
        PREFIX_FILENAME = "additional_"
        with open(env_file.FACTS_FOLDER + PREFIX_FILENAME + file, "w") as outfile:
            for thread in range(1, max_num_threads + 1):
                try:
                    with open(env_file.FACTS_FOLDER + "Thread-" + str(thread) + "_"  + PREFIX_FILENAME + file) as infile:
                        outfile.write(infile.read())
                    
                    os.remove(env_file.FACTS_FOLDER + "Thread-" + str(thread) + "_"  + PREFIX_FILENAME + file)

                except FileNotFoundError:
                    pass

    with open(env_file.EVALUATION_FOLDER + "evaluation.csv", "w") as outfile:
        for thread in range(1, max_num_threads + 1):
            try:
                with open(env_file.EVALUATION_FOLDER + "Thread-" + str(thread) + "_evaluation.csv") as infile:
                    outfile.write(infile.read())
                
                os.remove(env_file.EVALUATION_FOLDER + "Thread-" + str(thread) + "_evaluation.csv")

            except FileNotFoundError:
                pass


def usage():
    print("Usage:")
    print("python main.py <bridge_name>")
    print("")
    print("Bridges currently supported: ronin | nomad")


def main():
    try:
        if len(sys.argv) != 2:
            usage()

        if sys.argv[1] not in ["ronin", "nomad"]:
            raise Exception("Bridge not supported")


        confirm_api_keys_loaded()

        match sys.argv[1]:
            case "ronin":
                process_ronin_bridge()
            case "nomad":
                process_nomad_bridge()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
