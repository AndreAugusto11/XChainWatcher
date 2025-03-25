from utils.utils import get_api_key

###################################################
###### CHANGE PARAMETERS BASED ON THE BRIDGE ######
###################################################

## NOMAD BRIDGE PARAMETERS

SOURCE_CHAIN_CONNECTION_URL = "https://svc.blockdaemon.com/ethereum/mainnet/native"
SOURCE_CHAIN_CONNECTION_OPTIONS = {
    "headers": {
        "Authorization": f"Bearer {get_api_key('ETHEREUM_API_KEY')}",
        "Content-Type": "application/json",
    }
}

TARGET_CHAIN_CONNECTION_URL = f"https://rpc.ankr.com/moonbeam/{get_api_key('MOONBEAM_API_KEY')}"
TARGET_CHAIN_CONNECTION_OPTIONS = {
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
}

# CHAIN IDs
SOURCE_CHAIN_ID = 6648936     # Ethereum
TARGET_CHAIN_ID = 1650811245  # Moonbeam

MAX_NUM_THREADS_SOURCE_CHAIN = 15
MAX_NUM_THREADS_TARGET_CHAIN = 15

# Finality times of each chain or cross-chain protocol (like fraud-proof time window) in seconds
SOURCE_CHAIN_FINALITY_TIME = 1800
TARGET_CHAIN_FINALITY_TIME = 1800

# Name of files with transaction receipts
FILENAME_SOURCE_CHAIN_TRANSACTION_RECEIPTS = "./raw-data/nomad-bridge/tx_receipts/ethereum_selected_interval.json"
FILENAME_TARGET_CHAIN_TRANSACTION_RECEIPTS = "./raw-data/nomad-bridge/tx_receipts/moonbeam_selected_interval.json"

# Name of files with additional transaction
FILENAME_SOURCE_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS = "./raw-data/nomad-bridge/tx_receipts/ethereum_after_interval.json"
FILENAME_TARGET_CHAIN_ADDITIONAL_TRANSACTION_RECEIPTS = ""

# Name of files with block data receipts
FILENAME_SOURCE_CHAIN_BLOCK_DATA = "./raw-data/nomad-bridge/blocks/ethereum.csv"
FILENAME_TARGET_CHAIN_BLOCK_DATA = "./raw-data/nomad-bridge/blocks/moonbeam.csv"

ABIs_DIR = "./cross-chain-rules-validator/utils/ABIs/"
SC_ABIs_DIR = f"{ABIs_DIR}ethereum/"
TC_ABIs_DIR = f"{ABIs_DIR}moonbeam/"

# Bridge Address Source Chain (Ethereum) - Manager Proxy
SOURCE_CHAIN_BRIDGE_ADDRESS_DEPOSITS = "0x88a69b4e698a4b090df6cf5bd7b2d47325ad30a3"
SOURCE_CHAIN_BRIDGE_ADDRESS_WITHDRAWALS = "0x049b51e531fd8f90da6d92ea83dc4125002f20ef"
# Bridge Source Code Address (Ethereum) - Implementation Contracts
SOURCE_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE = "0x2d6775c1673d4ce55e1f827a0d53e62c43d1f304"
SOURCE_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS = "0xe0db61ac718f502B485DEc66D013afbbE0B52F84"
SOURCE_CHAIN_BRIDGE_SOURCE_CODE_WITHDRAWALS = "0x8407dc57739bcda7aa53ca6f12f82f9d51c2f21e"
SOURCE_CHAIN_ABI_CONTRACT_DEPOSITS = f"{ABIs_DIR}ethereum/NOMAD-BRIDGE-DEPOSITS.json"
SOURCE_CHAIN_ABI_CONTRACT_WITHDRAWALS = f"{ABIs_DIR}ethereum/NOMAD-BRIDGE-WITHDRAWALS.json"


# Contract to which state proofs are relayed and fraud proofs are submitted on the source chain
SOURCE_CHAIN_ABI_HOME_CONTRACT="0x92d3404a7e6c91455bbd81475cd9fad96acff4c8"
SOURCE_CHAIN_SOURCE_CODE_HOME_CONTRACT="0xf3bb7e2d4b26ae2c3eac41171840c227f457ea06"

# Bridge Address Target Chain (Moonbeam) - Manager Proxy
TARGET_CHAIN_BRIDGE_ADDRESS_DEPOSITS = "0x7f58bb8311db968ab110889f2dfa04ab7e8e831b"
TARGET_CHAIN_BRIDGE_ADDRESS_WITHDRAWALS = "0xd3dfd3ede74e0dcebc1aa685e151332857efce2d"
# Bridge Source Code Address (Moonbeam) - Implementation Contract
TARGET_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS_NATIVE = "0xb70588b1a51f847d13158ff18e9cac861df5fb00"
TARGET_CHAIN_BRIDGE_SOURCE_CODE_DEPOSITS = "0x8d2c231c3522b9906b4e017c9ad658868720b436"
TARGET_CHAIN_BRIDGE_SOURCE_CODE_WITHDRAWALS = "0x0e6a3fd785f2169a086e179004710ba6b663a892"
TARGET_CHAIN_ABI_CONTRACT_DEPOSITS = f"{ABIs_DIR}moonbeam/NOMAD-BRIDGE-DEPOSITS.json"
TARGET_CHAIN_ABI_CONTRACT_WITHDRAWALS = f"{ABIs_DIR}moonbeam/NOMAD-BRIDGE-WITHDRAWALS.json"

# Contract to which state proofs are relayed and fraud proofs are submitted on the source chain
TARGET_CHAIN_ABI_HOME_CONTRACT="0x8f184d6aa1977fd2f9d9024317d0ea5cf5815b6f"
TARGET_CHAIN_SOURCE_CODE_HOME_CONTRACT="0x5b70013fbeb1211a23ea33eb681ec87196475805"

# ETH is the native token in the Source Chain (Ethereum). We need the contract of the wrapped version
CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_SOURCE_CHAIN = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

# AXS is the native token in the Target Chain (Moonbeam). We need the contract of the wrapped version
CONTRACT_ADDRESS_EQUIVALENT_NATIVE_TOKEN_TARGET_CHAIN = "0xacc15dc74880c9944775448304b263d191c6077f"

# Token Mappings between Source Chain (Ethereum) and Target Chain (Moonbeam) according to the documentation and code
# in the form [SOURCE_CHAIN_ID, TARGET_CHAIN_ID, TOKEN_ADDRESS_SOURCE_CHAIN, TOKEN_ADDRESS_TARGET_CHAIN, STANDARD]
TOKEN_MAPPINGS = [
    [6648936, 1650811245, "0xba8d75baccc4d5c4bd814fde69267213052ea663", "0xacc15dc74880c9944775448304b263d191c6077f", 20], #WGLMR
    [6648936, 1650811245, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "0x8f552a71efe5eefc207bf75485b356a0b3f01ec9", 20], #USDC
    [6648936, 1650811245, "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "0x30d2a9f5fdf90ace8c17952cbb4ee48a55d916a7", 20], #WETH
    [6648936, 1650811245, "0xeb4c2781e4eba804ce9a9803c67d0893436bb27d", "0xcb8dbb3040b347705aca307ca562c209d3466fb6", 20], #renBTC
    [6648936, 1650811245, "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "0x1dc78acda13a8bc4408b207c9e48cdbc096d95e0", 20], #WBTC
    [6648936, 1650811245, "0x6b175474e89094c44da98b954eedeac495271d0f", "0xc234a67a4f840e61ade794be47de455361b52413", 20], #DAI 
    [6648936, 1650811245, "0xdac17f958d2ee523a2206206994597c13d831ec7", "0x8e70cd5b4ff3f62659049e74b6649c6603a0e594", 20], #USDT
    [6648936, 1650811245, "0xd417144312dbf50465b1c641d016962017ef6240", "0x5130ca61bf02618548dfc3fdef50b50b36b11f2b", 20], #CQT
    [6648936, 1650811245, "0x853d955acef822db058eb8505911ed77f175b99e", "0x8d6e233106733c7cc1ba962f8de9e4dcd3b0308e", 20], #FRAX
    [6648936, 1650811245, "0x0bf0d26a527384bcc4072a6e2bca3fc79e49fa2d", "0xf42bd09c48498afa3993c00e226e97841d5789a7", 20], #MYT
    [6648936, 1650811245, "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0", "0x21a8daca6a56434bdb6f39e7616c0f9891829aec", 20], #FXS
]

# All addresses of bridge contracts that are controlled by the bridge
BRIDGE_CONTROLLED_ADDRESSES = [
    [6648936,	"0x88a69b4e698a4b090df6cf5bd7b2d47325ad30a3"],
    [6648936,	"0x049b51e531fd8f90da6d92ea83dc4125002f20ef"],
    [6648936,	"0x2d6775c1673d4ce55e1f827a0d53e62c43d1f304"],
    [6648936,	"0xa5924d9baa4fed0fbd100cb47cbcb61ea5e33219"],
    [6648936,	"0x5d94309e5a0090b165fa4181519701637b6daeba"],
    [6648936,	"0x0000000000000000000000000000000000000000"],
    [1650811245,	"0xd3dfd3ede74e0dcebc1aa685e151332857efce2d"],
    [1650811245,	"0x7f58bb8311db968ab110889f2dfa04ab7e8e831b"],
    [1650811245,	"0xb70588b1a51f847d13158ff18e9cac861df5fb00"],
    [1650811245,	"0x0000000000000000000000000000000000000000"],
]

###################################################
######   DATALOG ENGINE RELATED PARAMETERS   ######
###################################################

# Datalog facts folder
FACTS_FOLDER = './cross-chain-rules-validator/datalog/nomad-bridge/facts/'

# The folder to which the evaluation results will be saved
EVALUATION_FOLDER = "./cross-chain-rules-validator/evaluations/nomad-bridge/"
