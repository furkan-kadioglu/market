
# coding: utf-8

# In[1]:
import numpy
import psycopg2
import pandas as pd 
import alphalens as alpha
#get_ipython().run_line_magic('pylab', 'inline')

currency = pd.read_csv('all_currencies.csv',
                        parse_dates = ['Date'],
                        index_col = ['Date'],
                        usecols = ['Date','Symbol','Close','Market Cap','Volume'])
currency['Market Cap'] = currency['Market Cap'].fillna(0)
currency.sort_index(inplace = True)


df_prices = (currency
             .reset_index()
             .pivot_table(index = 'Date', columns = 'Symbol', values = 'Close'))
df_prices.fillna(0,inplace=True)


# In[2]:


def chain_frame(df_trades,df_holdings,df_values,df_port,cash_port):
    
    df_holdings = (df_trades
                   .cumsum())
    
    df_values = (df_prices 
                 * df_holdings)
    df_port = (df_values
               .sum(axis = 1))
    


    return {'df_trades' : df_trades,
            'df_holdings' : df_holdings, 
            'df_values' : df_values, 
            'df_port' : df_port,
            'cash_port' : cash_port}


# In[4]:


'''def calculate_cost(symbol_cost,date_cost):
    
    buy_order = df_orders.loc[
        ((df_orders['Symbols']==symbol_cost)&
        (df_orders['Orders']=='BUY')&
        (df_orders.index<=date_cost))].Shares
    sell_order = df_orders.loc[
        ((df_orders['Symbols']==symbol_cost)&
        (df_orders['Orders']=='SELL')&
        (df_orders.index<=date_cost))].Shares
    sell_sum = np.sum(sell_order)
    buy_sum = np.sum(buy_order)
    

    if buy_sum > sell_sum:
        rest_prices = df_prices.reindex(buy_order.index)
        rest_prices = rest_prices[symbol_cost].loc[rest_prices.index<=date_cost]
        if sell_sum == 0:
            return (buy_order * rest_prices).sum() 
        buy_cum = buy_order.cumsum()
        len_of_sell = len(buy_cum[buy_cum<sell_sum])
        sell_sum -= buy_cum[len_of_sell-1]
        buy_order[buy_order.index<buy_order.index[len_of_sell]]=0
        buy_order[len_of_sell] -= sell_sum
        cost_series = buy_order * rest_prices
        return cost_series.sum()
    elif buy_sum < sell_sum:
        rest_prices = df_prices.reindex(sell_order.index)
        rest_prices = rest_prices[symbol_cost].loc[rest_prices.index<=date_cost]
        if buy_sum == 0:
            return -1 * (sell_order * rest_prices).sum() 
        sell_cum = sell_order.cumsum()
        len_of_buy = len(sell_cum[sell_cum<buy_sum])
        buy_sum -= sell_cum[len_of_buy-1]
        sell_order[sell_order.index<sell_order.index[len_of_buy]]=0
        sell_order[len_of_buy] -= buy_sum
        cost_series = sell_order * rest_prices
        return_cost = (-1) * cost_series.sum()
        return return_cost
    else:
        return 0
        '''


# In[5]:


def market_cap(date_weight,
                       freq,
                       universe):
    
    weight_frame = (currency.pivot_table(index = currency.index, columns = currency.Symbol, values = 'Market Cap')
                    [universe.index.unique().tolist()]
                    .loc[date_weight])
    
    weight_frame = (weight_frame
                    .fillna(0)
                    .sort_index())
        
    weight_frame = (weight_frame / weight_frame.sum()).round(2)
    #print(weight_frame.sum())
    weight_frame = weight_frame / weight_frame.sum()
    #print(weight_frame)

    return weight_frame.reindex(currency.Symbol.unique()).fillna(0)


# In[6]:


def trading_differences(date_diff,
                        frame_weight, 
                        universe, 
                        vol, 
                        df_trades,df_holdings,df_values,df_port,cash_port):
    
    selected = universe.index 
    
    now_hold = (df_holdings
                .loc[date_diff]
                .sort_index())
    
    multiplier = df_port.loc[date_diff] 
    
    new_hold = ((frame_weight * multiplier) 
                / (df_prices
                   .loc[date_diff]
                   .reindex(selected)))
    
    diff = (new_hold - now_hold).fillna(0).to_frame(date_diff)

   
    
    
    return re_trade(date_diff, diff, vol, frame_weight, cash_port,universe)


# In[7]:


def re_trade(date_diff, diff, vol, frame_weight, cash_port,universe):
          

    vol_diff = diff[date_diff] - vol[date_diff]  

    if (vol_diff <= 0).all():
        return {'diff' : diff, 
                'cash_port' : cash_port}
    else:
        print('!!EXCESS!!')
        excess = vol_diff.loc[vol_diff > 0] 
        
        success_trades = (vol_diff
                          .loc[vol_diff <= 0]
                          .reindex(universe.index)
                          .dropna())

        if vol_diff.sum() > 0 :

            cash_port.loc[date_diff] = vol_diff.sum()  
            print('!!WARNING OF OVERVOLUME!!')
            return {'diff' : vol, 
                    'cash_port' : cash_port}
         
        diff.loc[excess.index] = vol.loc[excess.index]
         

        multiplier = excess.sum()
        frame_weight.loc[excess.index] = 0
        frame_weight.loc[success_trades.index] = (1.0 / (len(success_trades)))
        
        #frame_weight = frame_weight * (1.0 / frame_weight.sum())
        diff_update = ((frame_weight * multiplier)
                       / (df_prices
                          .loc[date_diff]
                          .to_frame(date_diff)))
        
        diff += diff_update

        return re_trade(date_diff, diff, vol, frame_weight, cash_port, universe)
        
        


# In[8]:


def rebalance(date_bal,weight_func,freq,df_trades,df_holdings,df_values,df_port, cash_port):
    
    universe = (currency.pivot_table(index = 'Date',
                                     columns = 'Symbol',
                                     values = 'Market Cap')
                .loc[date_bal]
                .fillna(0)
                .nlargest(10)
                .sort_index()
                .to_frame(date_bal))
      
    vol = (currency.pivot_table(index = 'Date', 
                                columns = 'Symbol', 
                                values = 'Volume')
           .loc[date_bal]
           .fillna(0)
           .to_frame(date_bal)) #series index = symbol
     
    weight_fra = weight_func(date_bal,freq ,universe)
    #print(weight_fra)
    
    trade_dic = trading_differences(date_bal,
                                    weight_fra,
                                    universe,
                                    vol,
                                    df_trades,df_holdings,df_values,df_port,cash_port)
    
    
    #print(weight_fra[weight_fra[date_bal] > 0])
    new_trade = trade_dic['diff']
    cash_port = trade_dic['cash_port'] 
    df_trades.loc[date_bal] = new_trade[date_bal]
    
    return {'df_trades' : df_trades,
            'df_holdings' : df_holdings, 
            'df_values' : df_values, 
            'df_port' : df_port, 
            'cash_port' : cash_port}


# In[9]:


def plot_port(date_freq,df_port,cash_port,name):
    

    rest_port = df_port + cash_port.cumsum()
    
    rest_port.plot(label = name,figsize = (17,12))
    #print(rest_port.pct_change().std())
    #rest_port.plot(figsize = (17,12))


# In[3]:


def sql(name,dataFrame):
    from sqlalchemy import create_engine
    
    dataFrame = (dataFrame
                 .reset_index()
                 .melt(id_vars='Date',
                       value_vars=dataFrame.columns,
                       var_name='Symbol',
                       value_name='Value'))
    
    #create or replace the table 
    engine = create_engine('postgresql://postgres:admin@localhost:5432/postgres')
    pd.DataFrame(columns=['Date','Symbol','Value']).to_sql(name, engine,index=False,if_exists='replace')
    
    
    connection = psycopg2.connect(dbname='postgres',
                                  user='postgres',
                                  password='admin',
                                  host='localhost',
                                  port='5432')
    
    cursor = connection.cursor()
    for index, row in dataFrame.iterrows():
        row_dict = row.to_dict()
        row_dict["table_name"] = psycopg2.extensions.AsIs(name)
        cursor.execute("INSERT INTO %(table_name)s VALUES(%(Date)s, %(Symbol)s, %(Value)s)", row_dict),
    connection.commit()
    connection.close()

# In[10]:


def backtest(freq_test,initial_money,st_date,end_date,weight_func):
    df_trades = pd.DataFrame(0,index = currency.index.unique(), columns = sorted(currency.Symbol.unique()))
    df_holdings = ({})
    df_values = ({})
    df_port = ({})
    cash_port = ({})
    range_of_test = pd.date_range(st_date,end_date,freq = freq_test)
    cash_port = pd.Series(index = currency.index.unique(), data=0)
    
    dic = {'df_trades' : df_trades,
           'df_holdings' : df_holdings, 
           'df_values' : df_values, 
           'df_port' : df_port, 
           'cash_port' : cash_port}
    dic = chain_frame(**dic)
    dic['df_port'].loc[range_of_test[0]] = initial_money
    dic['cash_port'].loc[st_date] = initial_money
    dic['cash_port'].loc[range_of_test[0]] = initial_money * (-1)
    for arg in range_of_test :
        #print(dic['df_port'].loc[arg])
        #print(arg)
        dic = rebalance(arg,weight_func,freq_test,**dic) 
        #print(dic['cash_port'])
        dic = chain_frame(**dic)
        #print(arg)
        #print(dic['df_port'].loc[arg])
        
    sql('trade',dic['df_trades'])
    #plot_port(range_of_test,dic['df_port'].loc[st_date:end_date],dic['cash_port'].loc[st_date:end_date],weight_func.__name__)
    #return dic['df_port'].loc[st_date:end_date] + dic['cash_port'].loc[st_date:end_date]


# In[11]:


def momentum (date_str, freq, universe):
    last_price = df_prices[universe.index].loc[date_str] #series
    initial_day = pd.bdate_range(end = date_str,freq = freq,periods =2)[0]
    first_price = df_prices[universe.index].loc[initial_day] #series
    
    target = (last_price / first_price)
    target[target == numpy.inf] = 0
    target = (target / target.sum())
    
    return target


# In[12]:


def analyze(start_date,end_date,period,func_of_strategy):
    def universe_reduction(p,date):
        
        all_cripto = set(currency
                      .Symbol
                      .unique())

        universe = (currency
                    .loc[date]
                    .set_index('Symbol')
                    ['Market Cap']
                    .nlargest(10)
                    .index)
        
        reducing_cripto = all_cripto.difference(universe)

        p.loc[reducing_cripto] = numpy.NaN
        
        return p
    
    prices = df_prices.copy()
    first = pd.bdate_range(end = start_date,freq = '7D',periods = 2)[0]
    
    if first not in prices.index:
        start_date = pd.date_range(start = '2013-4-28', freq = '7D',periods = 2)[-1] 
        print('WARNING STARTING DATE: ' + start_date)
    
    prices = prices.reindex(pd.date_range(start_date,end_date))    

    prices = prices.apply(lambda x: universe_reduction(x,x.name),axis = 1)

    factor = (prices
              .apply(lambda x: func_of_strategy(x.name, '7D',x).replace(0,numpy.NaN),axis = 1))
    
    factor = factor.transform(lambda x: pd.qcut(x,10,labels = False, duplicates = 'drop'),axis = 1)
    
    factor = factor.T.unstack()
    
    analysis_of_returns = alpha.utils.get_clean_factor_and_forward_returns(factor,
                                                     prices,
                                                     quantiles = None,
                                                     bins = 10,
                                                     periods = period,
                                                     max_loss=1.0,
                                                     filter_zscore = 2.0)
    
    alpha.tears.create_full_tear_sheet(analysis_of_returns)
    


# In[ ]:


backtest('M',1,'2016-12-2','2017-4-3',momentum)
#backtest('M',1,'2016-12-2','2017-4-3',market_cap)
#plt.show()
#backtest('M',1,'2017-4-28','2018-1-2',market_cap)
#(1 + df_prices['BTC'].loc['2016-5-4':].resample('7D').first().pct_change()).cumprod().plot(figsize = (17,12))

#plt.legend(fontsize = 15)


# In[ ]:


#analyze('2016-12-2','2017-4-3',(1,50,60),momentum)

