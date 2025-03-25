from utils.utils import get_api_key

###################################################
###### CHANGE PARAMETERS BASED ON THE BRIDGE ######
###################################################

## RONIN BRIDGE PARAMETERS

SOURCE_CHAIN_CONNECTION_URL = "https://svc.blockdaemon.com/ethereum/mainnet/native"
SOURCE_CHAIN_CONNECTION_OPTIONS = {
    "headers": {
        "Authorization": f"Bearer {get_api_key('ETHEREUM_API_KEY')}",
        "Content-Type": "application/json",
    }
}

TARGET_CHAIN_CONNECTION_URL = f"https://api-gateway.skymavis.com/rpc/archive?apikey={get_api_key('RONIN_CHAIN_API_KEY')}"
TARGET_CHAIN_CONNECTION_OPTIONS = {
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
}

# CHAIN IDs
SOURCE_CHAIN_ID = 1     # Ethereum
TARGET_CHAIN_ID = 2020  # Ronin

MAX_NUM_THREADS_SOURCE_CHAIN = 15
MAX_NUM_THREADS_TARGET_CHAIN = 15

# Finality times of each chain or cross-chain protocol (like fraud-proof time window) in seconds
SOURCE_CHAIN_FINALITY_TIME = 78
TARGET_CHAIN_FINALITY_TIME = 45

# Name of files with transaction receipts
FILENAME_SOURCE_CHAIN_TRANSACTION_RECEIPTS = "./raw-data/ronin-bridge/tx_receipts/ethereum_selected_interval.json"
FILENAME_TARGET_CHAIN_TRANSACTION_RECEIPTS = "./raw-data/ronin-bridge/tx_receipts/ronin_selected_interval.json"

# Name of files with additional transaction
FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS_BEFORE = "./raw-data/ronin-bridge/tx_receipts/ethereum_before_interval.json"
FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS_AFTER = "./raw-data/ronin-bridge/tx_receipts/ethereum_after_interval.json"
FILENAME_TARGET_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS = "./raw-data/ronin-bridge/tx_receipts/ronin_before_interval.json"

# Name of files with block data receipts
FILENAME_SOURCE_CHAIN_BLOCK_DATA = "./raw-data/ronin-bridge/blocks/ethereum.csv"
FILENAME_TARGET_CHAIN_BLOCK_DATA = "./raw-data/ronin-bridge/blocks/ronin.csv"

ABIs_DIR = "./cross-chain-rules-validator/utils/ABIs/"
SC_ABIs_DIR = f"{ABIs_DIR}ethereum/"
TC_ABIs_DIR = f"{ABIs_DIR}ronin/"

# Bridge Address Source Chain (Ethereum) - Manager Proxy
SOURCE_CHAIN_BRIDGE_ADDRESS = "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2"
# Bridge Source Code Address (Ethereum) - Implementation Contract
SOURCE_CHAIN_BRIDGE_SOURCE_CODE = "0x8407dc57739bcda7aa53ca6f12f82f9d51c2f21e"

# For the second deployment of the contract after the attack
SOURCE_CHAIN_BRIDGE_ADDRESS_V2 = "0x64192819ac13ef72bf6b5ae239ac672b43a9af08"
SOURCE_CHAIN_BRIDGE_SOURCE_CODE_V2 = "0x72e28a9009ad12de019bff418cd210d4bbc3d403"

# Bridge Address Target Chain (Ronin) - Manager Proxy
TARGET_CHAIN_BRIDGE_ADDRESS = "0xe35d62ebe18413d96ca2a2f7cf215bb21a406b4b"
# Bridge Source Code Address (Ronin) - Implementation Contract
TARGET_CHAIN_BRIDGE_SOURCE_CODE = "0xdfe976b707c84551b78e687d11ac6eb1334ec8b1"

# ETH is the native token in the Source Chain (Ethereum). We need the contract of the wrapped version
CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

# AXS is the native token in the Target Chain (Ronin). We need the contract of the wrapped version
CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN = "0x97a9107c1793bc407d6f527b77e7fff4d812bece"

# Token Mappings between Source Chain (Ethereum) and Target Chain (Moonbeam) according to the documentation and code
# in the form [SOURCE_CHAIN_ID, TARGET_CHAIN_ID, TOKEN_ADDRESS_SOURCE_CHAIN, TOKEN_ADDRESS_TARGET_CHAIN, STANDARD]
TOKEN_MAPPINGS = [
    [1, 2020, "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b", "0x97a9107c1793bc407d6f527b77e7fff4d812bece", 20],
    [1, 2020, "0xcc8fa225d80b9c7d42f96e9570156c65d6caaa25", "0xa8754b9fa15fc18bb59458815510e40a12cd2014", 20],
    [1, 2020, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "0x0b7007c13325c48911f73a2dad5fa5dcbf808adc", 20],
    [1, 2020, "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5", 20],
    [1,	2020, "0x0c7cf86188632e16af00415214155950684466a8",	"0x173a2d4fa585a63acd02c107d57f932be0a71bcc", 20]
]

# All addresses of bridge contracts that are controlled by the bridge
BRIDGE_CONTROLLED_ADDRESSES = [
    [1,	"0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2"],
    [1,	"0x64192819ac13ef72bf6b5ae239ac672b43a9af08"],
    [2020,	"0xe35d62ebe18413d96ca2a2f7cf215bb21a406b4b"],
]

###################################################
######   DATALOG ENGINE RELATED PARAMETERS   ######
###################################################

# Datalog facts folder
FACTS_FOLDER = './cross-chain-rules-validator/datalog/ronin-bridge/facts/'

# The folder to which the evaluation results will be saved
EVALUATION_FOLDER = "./cross-chain-rules-validator/evaluations/ronin-bridge/"
