'''Functions to support cryptoasset_report jupyter notebook'''
import pandas as pd
import altair as alt

def plot_ind(df, short_var, long_var):
    '''Returns a candlestick chart designed for crossover strategy use.
    Parameters:
        df: DataFrame
        short_var/long_var: str, indicator column names
    Returns:
        Altair Interactive Chart
    '''
    scales = alt.selection_interval(bind='scales')
    move_color=alt.condition(
            'datum.price_close - datum.price_open > 0',
            alt.value("#047220"),
            alt.value("#910513")
    )
    price = alt.Chart(df).mark_line(size=0.5).encode(
        alt.X('date:T', title='Date'),
        alt.Y('price_mean_a:Q', title='Arithmetic Mean Price')
    ).properties(width=600, title=df['base_asset_id'].iloc[0]
    ).add_selection(
        scales
    )
    candles1 = alt.Chart(df).mark_rule().encode(
        alt.X('date:T', title=None),
        alt.Y('price_low:Q', title=None),
        alt.Y2('price_high:Q', title=None),
        color=move_color
    )
    candles2 = alt.Chart(df).mark_bar().encode(
        alt.X('date:T', title=None),
        alt.Y('price_open:Q', title=None),
        alt.Y2('price_close:Q', title=None),
        color=move_color
    )
    ind1 = alt.Chart(df).mark_line(
        color='#1967e5'
    ).encode(
        alt.X('date:T', title='Date'),
        alt.Y('{}:Q'.format(short_var), title=None)
    )
    ind2 = alt.Chart(df).mark_line(color='blue').encode(
        alt.X('date:T', title='Date'),
        alt.Y('{}:Q'.format(long_var), title=None)
    )
    return price + candles1 + candles2 + ind1 + ind2


def plot_ind_trade(df, trade_df, short_var, long_var):
    '''Returns a candlestick chart designed for trade on crossover analysis.
    Parameters:
        df: DataFrame
        trade_df: DataFrame
        short_var/long_var: str, indicator column names
    Returns:
        Altair Interactive Chart
    '''
    import pandas as pd
    threshold = pd.DataFrame([{'zero':0}])
    scales = alt.selection_interval(bind='scales')
    width = 600
    move_color=alt.condition(
            'datum.price_close - datum.price_open > 0',
            alt.value("#047220"),
            alt.value("#910513")
    )
    price = alt.Chart(df).mark_line(size=0.8).encode(
        alt.X('date:T', title='Date'),
        alt.Y('price_mean_a:Q', title='Arithmetic Mean Price')
    ).properties(width=width, height=400, title=df['base_asset_id'].iloc[0]
    ).add_selection(
        scales
    )
    candles = alt.Chart(df).mark_bar(opacity=0.2).encode(
        alt.X('date:T', title=None),
        alt.Y('price_open:Q', title=None),
        alt.Y2('price_close:Q', title=None),
        color=move_color
    )
    ind1 = alt.Chart(df).mark_line(
        color='#1967e5', opacity=0.9
    ).encode(
        alt.X('date:T', title='Date'),
        alt.Y('{}:Q'.format(short_var), title=None)
    )
    ind2 = alt.Chart(df).mark_line(color='blue', opacity=0.9).encode(
        alt.X('date:T', title='Date'),
        alt.Y('{}:Q'.format(long_var), title=None)
    )
    trade = alt.Chart(trade_df).mark_circle(size=100, opacity=1).encode(
        alt.X('date:T', title=None),
        alt.Y('price:Q', title=None),
        color=alt.Color('trade', title='Trade History')
    )

    portfolio = alt.Chart(trade_df).mark_line().encode(
        alt.X('date:T', title=None),
        alt.Y('return:Q', title='Cum. Returns')
    ).properties(height=100, width=width)
    asset_return = alt.Chart(df).mark_line().encode(
        alt.X('date:T', title=None),
        alt.Y('return:Q', title=None)
    ).properties(height=100, width=width)
    baseline = alt.Chart(threshold).mark_rule(
        size=1.25,
        color='black'
    ).encode(
        alt.Y('zero:Q', title=None)
    )

    price_collection = price + candles + ind1 + ind2 + trade
    portfolio_collection = portfolio + baseline + asset_return
    return price_collection & portfolio_collection

def trade_sim(df, short_var, long_var, price_var, asset_var, date_var='date'):
    import pandas as pd
    '''This function simulates a trade on a reversal from short_var/long_var.
    Parameters:
        df: DataFrame - Sorted increasing date, the price/indicator/date data
        short_var-date_var: str - column name for corresponding var
    Returns:
        record: DataFrame - index, date, trade decision, price, and profit.
    Notes: Reversal is value based, short drops through long is a sell. Record
        is only kept on trade positive dates. Suggest marker on trade, line for profit.
        Index and date returned are from original dataframe.
        In the name of speed, this uses itertuples (recal iterrows does not preserve type)
        thus names of columns must be accessible as attributes. (no spaces...)
    '''
    # Setup
    record = pd.DataFrame(columns=['index', 'date', 'trade', 'price', 'return', 'asset'])
    data = df.itertuples()
    cum_return = 0
    can_sell = False
    # Get first calculations
    item = next(data)
    price = getattr(item, price_var)
    asset = getattr(item, asset_var)
    date = getattr(item, date_var)
    short, long = getattr(item, short_var), getattr(item, long_var)
    was_above = short > long
    for item in data:
        index = item.Index
        price = getattr(item, price_var)
        date = getattr(item, date_var)
        short, long = getattr(item, short_var), getattr(item, long_var)
        is_above = short > long
        if was_above != is_above: # Reversal
            if was_above:
                if can_sell:
                    trade = 'sell'
                    cum_return += (price - bought_price)/bought_price
                    can_sell = False
            else:
                trade = 'buy'
                bought_price = price
                can_sell = True
            record = record.append({'index':index, 'date':date, 'trade':trade, 'price':price, 'return':cum_return, 'asset':asset}, ignore_index=True)
        else:
            trade = None
        was_above = is_above
    return record
