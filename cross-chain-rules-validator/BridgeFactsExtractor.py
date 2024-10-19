import os

class BridgeFactsExtractor:

    facts_folder = ""

    def __init__(self, facts_folder):
        self.facts_folder = facts_folder
        try:
            if not os.path.exists(facts_folder):
                os.makedirs(facts_folder)
        except:
            raise Exception("Not able to open file")

    def extract_facts_from_bridge(
            self,
            token_mappings,
            bridge_controlled_addresses,
            source_chain_id,
            target_chain_id,
            finality_source_chain,
            finality_target_chain,
            contract_address_eq_native_token_source_chain,
            contract_address_eq_native_token_target_chain
        ):
        bridge_controlled_addresses_facts   = open(self.facts_folder + "/bridge_controlled_address.facts",  "w")
        cctx_finality_facts                 = open(self.facts_folder + "/cctx_finality.facts",              "w")
        token_mapping_facts                 = open(self.facts_folder + "/token_mapping.facts",              "w")
        native_token_facts                  = open(self.facts_folder + "/wrapped_native_token.facts",               "w")
        errors                              = open(self.facts_folder + "/errors.txt",                       "w")

        print("Extracting facts from bridge...")

        try:
            # write each mapping to the file, see cross-chain-rules-validator/utils/nomad_env.py 
            for mapping in token_mappings:
                token_mapping_facts.write("%s\t%s\t%s\t%s\t%s\r\n" % (mapping[0], mapping[1], mapping[2], mapping[3], mapping[4]))
            
            # for now we are considering only one source chain and one destination chain
            native_token_facts.write("%s\t%s\r\n" % (source_chain_id, contract_address_eq_native_token_source_chain))
            native_token_facts.write("%s\t%s\r\n" % (target_chain_id, contract_address_eq_native_token_target_chain))

            cctx_finality_facts.write("%s\t%s\r\n" % (source_chain_id, finality_source_chain))
            cctx_finality_facts.write("%s\t%s\r\n" % (target_chain_id, finality_target_chain))

            for pair in bridge_controlled_addresses:
                bridge_controlled_addresses_facts.write("%s\t%s\r\n" % (pair[0], pair[1]))

        except Exception as e:
            errors.write("%s" % (e))

        finally:
            token_mapping_facts.close()
            native_token_facts.close()
            errors.close()