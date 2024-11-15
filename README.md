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
* R (to create and visualize figures): `brew install r`. To install required R packages, run `sudo Rscript -e 'install.packages(c("ggplot2", "scales", "dplyr", "gridExtra", "patchwork", "tidyr", "lubridate", "cowplot"), repos="https://cloud.r-project.org")'`.
  
### Setup
1. Copy the raw data from a remote repository `gdown 1YeBQpXWUB8LEXkbzyF0uJqOfhxqKiby7 --folder`
1. Create a file `.env` from `.env.example`: `cp .env.example .env`
2. Create a file `./vscode/launch.json` from `.vscode/launch.example.json`: `cp .vscode/launch.example.json .vscode/launch.json`
3. Populate env vars, namely `MOONBEAM_API_KEY` ([you can obtain a free api key at onfinality](https://app.onfinality.io)), and `BLOCKDAEMON_API_KEY` (([you can obtain a free api key at Blockdaemon](https://app.blockdaemon.com/))).
4. `brew install --HEAD souffle-lang/souffle/souffle`
5. python3.11 -m venv xchainwatcherenv
6. source xchainwatcherenv/bin/activate
Full installation procedures, including for other OSs [is available in the official installation page](https://souffle-lang.github.io/install).
    `pip install -r requirements.txt`
7. To stop using the pip env, run `deactivate`
 
### Usage
🚨 Ronin related analysis is WIP (we are uploading the datasets) 🚨

#### Using VSCode
1. Open the project in VS Code.
2. Make sure you have the Python extension installed.
3. Open the Command Palette (Cmd+Shift+P on macOS or Ctrl+Shift+P on Windows/Linux).
4. Type "Python: Select Interpreter" and choose the interpreter in your xchainwatcherenv virtual environment.
5. Open the Debug view (Ctrl+Shift+D or Cmd+Shift+D on Mac).
6. From the dropdown at the top of the Debug view, select either:

* "Python: cross-chain-rules-validator/main.py with ronin flag (xchainwatcherenv)" for Ronin
* "Python: cross-chain-rules-validator/main.py with nomad flag (xchainwatcherenv)" for Nomad

Click the green play button or press F5 to start debugging.

#### Using Terminal

1. Activate the virtual environment if it's not already activated: `source xchainwatcherenv/bin/activate`
2. Navigate to the project root directory.
3. Run the script with the appropriate flag, `python cross-chain-rules-validator/main.py ronin` or `python cross-chain-rules-validator/main.py nomad` for Ronin or Nomad, respectively. 

When you're done, you can deactivate the virtual environment by running `deactivate`

#### Running the Cross-Chain Model
Run the following command to execute the cross-chain model with the previously extracted facts. The file contains acceptance rules that define the expected behavior within the selected interval, and imports several other files with facts definition and additional rules. The output of these rules are facts that comply with the model.

For the Ronin bridge:
```bash
souffle -p ./cross-chain-rules-validator/evaluations/ronin-bridge/datalog-logs.console -F./cross-chain-rules-validator/datalog/ronin-bridge/facts/ -D./cross-chain-rules-validator/datalog/ronin-bridge/results/ ./cross-chain-rules-validator/datalog/acceptance-rules.dl
```

For the Nomad bridge:
```bash
souffle -p ./cross-chain-rules-validator/evaluations/nomad-bridge/datalog-logs.console -F./cross-chain-rules-validator/datalog/nomad-bridge/facts/ -D./cross-chain-rules-validator/datalog/nomad-bridge/results/ ./cross-chain-rules-validator/datalog/acceptance-rules.dl
```

#### Evaluating the execution of the Cross-Chain Model

For the Ronin bridge:
```bash
souffleprof ./cross-chain-rules-validator/evaluations/ronin-bridge/datalog-logs.console -j
```

For the Nomad bridge:
```bash
souffleprof ./cross-chain-rules-validator/evaluations/nomad-bridge/datalog-logs.console -j
```

These commands will create a file under `profiler_html` with the profiler data. There are already examples in the folder.

### Figures
To generate figures, run each corresponding R script in `analysis/figures`, for instance `Rscript data-visualizations/cctx-breaking-finality-nomad.R`. Alternatively, open the project in RStudio.

### Data
This project includes the first open-source dataset of over 81,000 cross-chain transactions across three blockchains, capturing $585M and $3.7B in token transfers in Nomad and Ronin, respectively.

Datasets can be found under different folders. For Ronin and Nomad, respectively: raw data can be found in `cross-chain-rules-validator/analysis/ronin-bridge/data` and `cross-chain-rules-validator/analysis/nomad-bridge/data`. Datalog engine runs can be found in `cross-chain-rules-validator/datalog/ronin-bridge/results` and `cross-chain-rules-validator/datalog/nomad-bridge/results`. Datalog facts can be found in `cross-chain-rules-validator/datalog/ronin-bridge/facts` and `cross-chain-rules-validator/datalog/nomad-bridge/facts`.

### token-price-data
Token price data is an util that processes token data information for usage in the figure generation.

### Contributing
We adhere to the [Hyperledger Cacti contributing](https://github.com/hyperledger/cacti/blob/main/CONTRIBUTING.md) guidelines. Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

### License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


### Suggested Citation
This work is an implementation of the paper XChainWatcher. It can be obtained here:
```bibtex
@misc{augusto2024xchainwatcher,
      title={XChainWatcher: Monitoring and Identifying Attacks in Cross-Chain Bridges}, 
      author={André Augusto and Rafael Belchior and Jonas Pfannschmidt and André Vasconcelos and Miguel Correia},
      year={2024},
      eprint={2410.02029},
      archivePrefix={arXiv},
      primaryClass={cs.CR},
      url={https://arxiv.org/abs/2410.02029}, 
}
```

### Contact
For bugs, feature requests, and other issues, please use the GitHub issue tracker.

### Team
André Augusto (maintainer)
Rafael Belchior (contributor)