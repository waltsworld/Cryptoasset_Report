class Indicators():
    '''Include new features
    These are applied across all assets, by asset.
    Note on Moving Averages:
        They relate either to technical or value approaches as far as I can tell.
        I personally would like to investigate the change of valuation using crossover.
    '''
    def __init__(self, market, periods_dict=None):
    # Periods dictionary
        if not periods_dict:
            self.periods = {
                'sma':5,
                'sma_long':8,
                'ema':13,
                'ema_long':21,
                'wilder_rsi':14
                # all hail the fib sequence
            }
        else:
            self.periods = periods_dict
        self.market = market

    def add_indicators(self):
        # Simple moving average
        self.market['sma_s'] = (self.market.groupby('base_asset_id')
                                .apply(lambda x: x['price_close']
                                .rolling(self.periods['sma']).mean())
                                .reset_index(level=0, drop=True))
        # Add long simple moving average for crossover
        self.market['sma_l'] =  (self.market.groupby('base_asset_id')
                                 .apply(lambda x: x['price_close']
                                 .rolling(self.periods['sma_long']).mean())
                                 .reset_index(level=0, drop=True))
        # Exponential moving average
        self.market['ema_s'] = (self.market.groupby('base_asset_id')
                                .apply(lambda x: x['price_close']
                                .ewm(span=self.periods['ema'],
                                     adjust=False).mean())
                                .reset_index(level=0, drop=True))
        # Long exponential moving average
        self.market['ema_l'] = (self.market.groupby('base_asset_id')
                                 .apply(lambda x: x['price_close']
                                 .ewm(span=self.periods['ema_long'],
                                      adjust=False).mean())
                                 .reset_index(level=0, drop=True))
        # Price Change
        self.market['change'] = (market.groupby('base_asset_id')
                                .apply(lambda x: x['price_close'].diff())
                                .reset_index(level=0, drop=True))

        # RSI Using Wilder's Smoothing Factor in an EMA based mean.
        name = 'wilder_rsi'
        self.market[name] = [np.nan]*self.market.shape[0]
        for item, group in self.market.groupby('base_asset_id'):
            # Wilder Smoothing included.
            U = group['change'].apply(lambda x: max(0, x)).ewm(alpha = 1/self.periods['wilder_rsi'], adjust=False).mean()
            D = group['change'].apply(lambda x: max(0, -x)).ewm(alpha = 1/self.periods['wilder_rsi'], adjust=False).mean()
            RS = (U/D).replace([np.inf, -np.inf], np.nan).fillna(0)
            RSI = (100 - 100/(1 + RS))
            self.market[name].update(RSI)
        return self.market.sort_values(by='date')

    def add_smas(self):
        '''Add or replace simple moving average columns'''
        self.market['sma_s'] = (self.market.groupby('base_asset_id')
                                .apply(lambda x: x['price_close']
                                .rolling(self.periods['sma']).mean())
                                .reset_index(level=0, drop=True))
        # Add long simple moving average for crossover
        self.market['sma_l'] =  (self.market.groupby('base_asset_id')
                                 .apply(lambda x: x['price_close']
                                 .rolling(self.periods['sma_long']).mean())
                                 .reset_index(level=0, drop=True))
        return self.market.sort_values(by='date')

    def add_emas(self):
        '''Add or replace exponential moving average columns'''
        # Exponential moving average
        self.market['ema_s'] = (self.market.groupby('base_asset_id')
                                .apply(lambda x: x['price_close']
                                .ewm(span=self.periods['ema'],
                                     adjust=False).mean())
                                .reset_index(level=0, drop=True))
        # Long exponential moving average
        self.market['ema_l'] = (self.market.groupby('base_asset_id')
                                 .apply(lambda x: x['price_close']
                                 .ewm(span=self.periods['ema_long'],
                                      adjust=False).mean())
                                 .reset_index(level=0, drop=True))
        return self.market.sort_values(by='date')
