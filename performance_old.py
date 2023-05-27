import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import requests,json
from datetime import datetime, time,timedelta
import plotly.express as px
from json_loader import json_load
from returnsDf import agg_df
import warnings
warnings.filterwarnings('ignore')
pd.options.display.float_format = '${:,.2f}'.format
one_day=timedelta(days=1)
st.set_page_config(page_title="SquareoffbotsPerformance",layout='wide')
st.markdown("""<style> div[role="listbox"] ul {
    background-color: rgb(229, 236, 122);
    }
    div[role="listbox"],option{
        float:right; 
    }
    #MainMenu {display:none;}
    footer {display:none !important}


</style>

"""
    
    ,unsafe_allow_html=True)

pnl_url=r'http://performance.squareoffbots.com/assets/json/sqbots_allData_21052021.json'
cap_url=r'http://performance.squareoffbots.com/assets/json/newCAp21052021.json'
charges_url=r'http://performance.squareoffbots.com/assets/json/charges.json'

query_params = st.experimental_get_query_params()
@st.cache(ttl=20*60*60)
def getResources1():
    charges_dic=requests.get(charges_url).json()
    # charges_dic=json_load('charges.json')
    pnl_data=requests.get(pnl_url).json()
    cap_data=requests.get(cap_url).json()
    pnl_df_t=pd.DataFrame.from_dict(pnl_data)
    cap_df_t=pd.DataFrame.from_dict(cap_data)
    pnl_df=pnl_df_t.T
    cap_df=cap_df_t.T    
    return charges_dic,pnl_data,cap_data,pnl_df,cap_df,query_params
charges_dic,pnl_data,cap_data,pnl_df,cap_df,query_params=getResources1()
# charges_dic=requests.get(charges_url).json()
botNameDic={"orb":"ORB","rsi":"RSI","it":"Intraday Trend","sh":"StopHunt","grb":"GRB","orb2pm":"ORB2pm","pcr":"NiftyOptionSelling","lapp":"Learnapp","bss":"BNF Straddle","nss":"Nifty Straddle","bos":"BNFOptionSelling","grbo":"GRB Options","bssr":"BNF Strangle","mlb":"ML Bot","bnfmon":"BNF ORB","mss":"1% Short Straddle (BNF)","mssn":"1% Short Straddle(NF)","dts":"Double Top"}
botCapitalDic={"orb":50000,"rsi":50000,"it":50000,"sh":50000,"grb":300000,"orb2pm":300000,"pcr":300000,"lapp":300000,"bss":300000,"nss":300000,"bos":300000,"grbo":150000,"bssr":300000,"bnfmon":150000,"mlb":400000,"mss":300000,"mssn":300000,"dts":150000}
curBots=['orb','rsi','it','grb','bss','grbo','bssr','bnfmon','mlb','mss','mssn','dts']
botName = query_params["bot"][0] if "bot" in query_params else None

botsList=list(botNameDic.keys())
if botName not in botsList:
    botName='bss'
botsList.remove('bss')
botsList=['bss']+botsList
if not botName:
    botName = st.selectbox('Select a Strategy',tuple(botsList))

@st.cache(ttl=20*60*60,suppress_st_warning=True,allow_output_mutation=True)
def strategy_statistics():
    ret_dic={}
    for botName in curBots:
        eq_bots=["orb","rsi","sh","it"]
        botFullName=botNameDic[botName]
        botCapital=botCapitalDic[botName]



        strat_pnl_Df=pnl_df[[botFullName]]
        strat_pnl_Df.dropna(inplace=True)
        strat_cap_df=cap_df[[botFullName]]
        #returns calculation
        strat_df=agg_df(strat_pnl_Df,strat_cap_df)
        ##PNL plot
        strat_df['pdTime']=pd.to_datetime(strat_df.index,format="%Y-%m-%d")
        strat_df.sort_values('pdTime',inplace=True)
        strat_df[botFullName+'_adj_PnL']=(botCapital/100)*strat_df[botFullName+' Returns'].astype(float)
        strat_df[botFullName+'_gross_PnL']=strat_df[botFullName+'_adj_PnL']
        charges_types=['Brokerage','TransactionCharges','ClearingCharges','STT','GST','SEBI','StampDuty','TotalCharges']
        def getCharges(x):
            notGotCharges=True
            original_date=x
            cDayObj=datetime.strptime(x,'%Y-%m-%d')
            direction=-1
            direction_counter=0
        
            while notGotCharges:
                try:            
                    return charges_dic[cDayObj.strftime('%Y%m%d')][botName.upper()+'_'+ct]

                except Exception as e:
                    direction_counter+=1
                    if direction_counter==10:
                        direction*=-1
                
                
                    cDayObj+=direction*one_day
                    continue
        for ct in charges_types:
            strat_df[ct]=strat_df.index.to_series().apply(lambda x:getCharges(x))
        i_fields=['PNL','Brokerage','TransactionCharges','ClearingCharges','STT','GST','SEBI','StampDuty','TotalCharges','net_PNL']



        ##xxx
        if botName in eq_bots:
            i_fields=["PNL"]
            strat_df['net_PNL']=strat_df[botFullName+'_gross_PnL']
        else:
            strat_df['net_PNL']=strat_df[botFullName+'_gross_PnL']-strat_df['TotalCharges']

        strat_df['net_rets']=100*strat_df['net_PNL']/botCapital
        strat_df["Time"]=strat_df.index
        strat_df['PNL']=strat_df[botFullName+'_adj_PnL']
        strat_df['cum_pnl']=strat_df[botFullName+'_adj_PnL'].cumsum()
        ##DRAWDOWN
        drawdown_df=strat_df.copy()
        drawdown_df.reset_index(drop=True,inplace=True)
        drawdown_df['max_value_so_far']=drawdown_df['cum_pnl'].cummax()
        drawdown_df['drawdown']=drawdown_df['cum_pnl']-drawdown_df['max_value_so_far']
        max_drawdown=drawdown_df['drawdown'].min()
        ##Strategy statistics .
        stats_Df=pd.DataFrame(columns=["Total Days","Winning Days","Losing Days","Winning Accuracy(%)","Max Profit","Max Loss","Max Drawdown","Average Profit on Win Days","Average Profit on loss days","Average Profit Per day","Gross Profit","Charges","Net profit","Returns (%)","net Returns (%)"])
        total_days=len(strat_df)
        win_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')>0]
        lose_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')<0]
        noTrade_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')==0]
        win_days=len(win_df)
        lose_days=len(lose_df)
        win_ratio=win_days*100.0/(lose_days+win_days)
        max_profit=strat_df[botFullName+'_adj_PnL'].max()
        max_loss=strat_df[botFullName+'_adj_PnL'].min()
        # max_drawdown=0
        win_average_profit=win_df[botFullName+'_adj_PnL'].sum()/win_days
        loss_average_profit=lose_df[botFullName+'_adj_PnL'].sum()/lose_days
        total_profit=strat_df[botFullName+'_adj_PnL'].sum()

        if botName not in eq_bots:
            total_charges=strat_df['TotalCharges'].sum()
        else:
            total_charges=0
        net_profit=total_profit-total_charges
        average_profit=total_profit/total_days
        gross_returns=strat_df[botFullName+' Returns'].sum()
        net_returns=strat_df['net_rets'].sum()
        results_row=[total_days,win_days,lose_days,win_ratio,max_profit,max_loss,max_drawdown,win_average_profit,loss_average_profit,average_profit,total_profit,total_charges,net_profit,gross_returns,net_returns]
        results_row=[results_row[i] if i<3 else round(results_row[i],2) for i in range(len(results_row)) ]
        stats_Df.loc[0,:]=results_row
        t_stats_Df=stats_Df.T
        t_stats_Df.rename(columns={0:''},inplace=True)
        fig=px.line(strat_df, x="Time", y='cum_pnl', title=botFullName+' PNL',width=800, height=400)
        dd_fig=px.line(drawdown_df,x="Time",y="drawdown", title=botFullName+' PNL',width=800, height=400)
        strat_df['month']=strat_df['pdTime'].apply(lambda x:x.strftime('%b,%Y'))
        month_groups=strat_df.groupby('month',sort=False)[i_fields].sum()
        ##last 30 days pnl
        strat_df=strat_df.reindex(strat_df.index[::-1])
        if botName in eq_bots:
            capital_used_appendum=''
        else:    
            capital_used_appendum=' per Lot' 

        ret_dic[botName]=[botCapital,capital_used_appendum,results_row,t_stats_Df,fig,dd_fig,month_groups,strat_df,i_fields,botFullName]
    return ret_dic
ret_dic=strategy_statistics()
botCapital,capital_used_appendum,results_row,t_stats_Df,fig,dd_fig,month_groups,strat_df,i_fields,botFullName=ret_dic[botName]
title_text="<h1 style='text-align: center; color: rgb(21, 86, 112);'>**♟**SQUAREOFF BOTS PERFORMANCE**♟**</h1><br><div style='text-align: center; color: rgb(21, 86, 112);'>**LIVE PERFORMANCE OF "+botFullName+"****[Capital used is "+str(botCapital)+capital_used_appendum+"]** </div>"
st.markdown(title_text, unsafe_allow_html=True)



if botCapital>50000 and botName!='mlb':
    # col1.write("**(Capital used before July 2021 is "+str(int(botCapital/1.5))+capital_used_appendum+")**")
    st.markdown("<div style='text-align: center; color: rgb(21, 86, 112);'>**(Capital used before July 2021 is "+str(int(botCapital/1.5))+capital_used_appendum+")** </div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
col2.markdown('##')

col1.write("Net ROI : "+str(results_row[-1])+"%")
col1.write("**Statistics**")
col1.table(t_stats_Df)



col2.write("**PNL Curve**")
col2.plotly_chart(fig)
col2.write("**Drawdown Curve**")
col2.plotly_chart(dd_fig)
st.write("**Month-wise PNL**")
st.table(month_groups)
st.write("**Date-wise PNL (Last 30 Days)**")
st.table(strat_df[i_fields][:30])




##TABLE
# fig2=go.Figure(data=[go.Table(
#     header=dict(values=['Date','BSS'],
#                 fill_color='white',
#                 line_color='black',
               
#                 align='left'),
#     cells=dict(values=[strat_df.index,strat_df[botFullName+'_adj_PnL']],
#                fill_color='white',
               
             
#                align='left'))])
# st.plotly_chart(fig2)