import pandas as pd

# load dst_ethereum_addresses.csv
dst_ethereum_addresses = pd.read_csv('dst_ethereum_addresses_with_ether.csv')

# remove column called dst_address_balance_at_date and dst_address_balance_today
dst_ethereum_addresses = dst_ethereum_addresses.drop(columns=['dst_address_balance_at_date', 'dst_address_balance_today'])

# save the result to dst_ethereum_addresses_v2.csv
dst_ethereum_addresses.to_csv('dst_ethereum_addresses_with_ether.csv', index=False)