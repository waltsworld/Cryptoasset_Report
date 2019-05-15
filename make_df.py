
def man_join(market, blockchain):
    import pandas as pd
    market_assets = list(market['base_asset_id'].astype('category').cat.categories)
    block_assets = list(blockchain['asset_id'].astype('category').cat.categories)
    target_assets = [i for i in market_assets if i in block_assets]
    selected_market = market[market['base_asset_id'].isin(target_assets)]
    composite = selected_market.merge(blockchain, how='outer', left_on=['base_asset_id', 'date'], right_on=['asset_id','date'])
    composite.sort_values(by='date')
    return composite


if __name__=='__main__':
    import pandas as pd
    blockchain = pd.read_csv('data/blockchain_data.csv')
    market = pd.read_csv('data/market_data.csv')
    # Prepare Market Data
    market['date'] = market['epoch_ts'].astype('datetime64[ns]')
    market.sort_values(by='date', inplace=True) # Increasing date for rolling calculations
    market.drop(columns='epoch_ts', inplace=True)
    # Prepare Blockchain Data
    blockchain['date'] = blockchain['epoch_ts'].astype('datetime64[ns]')
    blockchain.sort_values(by='date', inplace=True) # Increasing date for rolling calculations
    blockchain.drop(columns='epoch_ts', inplace=True)

    composite = man_join(market, blockchain)
