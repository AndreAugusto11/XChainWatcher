# XChainWatcher

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub issues](https://img.shields.io/github/issues/AndreAugusto11/XChainWatcher)](https://github.com/AndreAugusto11/XChainWatcher/issues) [![GitHub stars](https://img.shields.io/github/stars/AndreAugusto11/XChainWatcher)](https://github.com/AndreAugusto11/XChainWatcher/stargazers)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Datalog](https://img.shields.io/badge/Datalog-powered-brightgreen)](https://en.wikipedia.org/wiki/Datalog) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/AndreAugusto11/XChainWatcher/blob/main/CONTRIBUTING.md)

XChainWatcher is a pluggable monitoring and detection mechanism for cross-chain bridges, powered by a cross-chain model. It uses the [Souffle Datalog engine](https://souffle-lang.github.io/) to identify deviations from expected behavior defined in terms of cross-chain rules.

Here's an example of a basic cross-chain transaction rule:
```
ValidCCTX_Rule1(asset_id, tx_hash_A, tx_hash_B) :-
    Transaction(A, tx_hash_A, timestamp_tx_a),
    Transaction(B, tx_hash_B, timestamp_tx_b),
    LockAsset(asset_id, tx_hash_A),
    MintAsset(asset_id, tx_hash_B),
    timestamp_tx_b > timestamp_tx_a + δ
```

This rule defines a valid cross-chain transaction where an asset is locked on one chain and minted on another, with appropriate time constraints.

### Key Features
1. Monitoring of cross-chain transactions
2. Detection of attacks and unintended behavior in cross-chain bridges
3. Analysis of transaction data from multiple blockchains
4. Pluggable design for integration with various cross-chain bridges

### Key Findings
Our analysis using XChainWatcher has revealed:

* Successful identification of transactions leading to losses of $611M and $190M USD in the Ronin and Nomad bridges, respectively.
* Discovery of 37 cross-chain transactions that these bridges should not have accepted.
* Identification of over $7.8M locked on one chain but never released on Ethereum. 
* Detection of $200K lost due to inadequate interaction with bridges.

See the full paper for details. These findings demonstrate the critical need for robust monitoring and analysis tools in the cross-chain bridge ecosystem.

### Project structure

```
.
├── analysis/                 # R scripts for data analysis
│   └── figures/              # Generated figures and plots
├── cross-chain-rules-validator/
│   ├── analysis/             # Jupyter notebooks for bridge-specific analysis
│   ├── datalog/              # Datalog rules and facts
│   │   ├── lib/              # Datalog library files
│   │   ├── nomad-bridge/     # Nomad bridge specific facts and results
│   │   └── ronin-bridge/     # Ronin bridge specific facts and results
│   └── utils/                # Utility functions and ABIs
│       └── ABIs/             # ABI files for various contracts
├── BridgeFactsExtractor.py   # Base class for extracting bridge facts
├── FactsExtractor.py         # Main facts extractor
├── NomadFactsExtractor.py    # Nomad-specific facts extractor
├── RoninFactsExtractor.py    # Ronin-specific facts extractor
└── main.py                   # Main entry point of the application
```

### Requirements
* [python 3.11](https://www.python.org/downloads/release/python-3115/): `brew install python@3.11` (tested with python 3.11.5)
* Virtualenv: `pip install virtualenv`
* R (to create and visualize figures): `brew install r`. To install required R packages, run `sudo Rscript -e 'install.packages(c("ggplot2", "scales", "dplyr", "gridExtra", "patchwork", "tidyr", "lubridate"), repos="https://cloud.r-project.org")'`.
  
### Setup
1. Create a file `.env` from `.env.example`: `cp .env.example .env`
2. Populate env vars, namely `MOONBEAM_API_KEY` ([you can obtain a free api key at onfinality](https://app.onfinality.io)), and `BLOCKDAEMON_API_KEY` (([you can obtain a free api key at Blockdaemon](https://app.blockdaemon.com/))). You may set `SOURCE_CHAIN_API_KEY`and `TARGET_CHAIN_API_KEY` to the same value as `BLOCKDAEMON_API_KEY`.
3. `brew install --HEAD souffle-lang/souffle/souffle`
4. python3.11 -m venv xchainwatcherenv
5. source xchainwatcherenv/bin/activate
Full installation procedures, including for other OSs [is available in the official installation page](https://souffle-lang.github.io/install).
    `pip install -r requirements.txt`

### Usage
🚨 Ronin related analysis is WIP (we are uploading the datasets) 🚨



#### Figures
To generate figures, run each corresponding R script in `analysis/figures`, for instance `Rscript analysis/cctx-breaking-finality-nomad.R`.

### Data
This project includes the first open-source dataset of over 81,000 cross-chain transactions across three blockchains, capturing $585M and $3.7B in token transfers in Nomad and Ronin, respectively.

Datasets can be found under different folders. For Ronin and Nomad, respectively: raw data can be found in `cross-chain-rules-validator/analysis/ronin-bridge/data` and `cross-chain-rules-validator/analysis/nomad-bridge/data`. Datalog engine runs can be found in `cross-chain-rules-validator/datalog/ronin-bridge/results` and `cross-chain-rules-validator/datalog/nomad-bridge/results`. Datalog facts can be found in `cross-chain-rules-validator/datalog/ronin-bridge/facts` and `cross-chain-rules-validator/datalog/nomad-bridge/facts`.

### Contributing
We adhere to the [Hyperledger Cacti contributing](https://github.com/hyperledger/cacti/blob/main/CONTRIBUTING.md) guidelines. Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

### License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


### Suggested Citation
This work is an implementation of the paper XChainWatcher. It can be obtained here:
TBD

### Contact
For bugs, feature requests, and other issues, please use the GitHub issue tracker.

### Team
André Augusto (maintainer)
Rafael Belchior (contributor)