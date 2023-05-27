import pandas as pd
from pandas import Timestamp
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import requests,json
from datetime import datetime, time,timedelta
import plotly.express as px
import warnings
import io
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


query_params = st.experimental_get_query_params()
# st.runtime.legacy_caching.clear_cache()
@st.cache(ttl=3*60*60)
def get_ret_dic():
    streamlit_data_url=r'https://dailysymbols.s3.ap-south-1.amazonaws.com/streamlit_data_ppl.json'
    ret_dic=requests.get(streamlit_data_url).json()
    return ret_dic
# def get_ret_dic():
#     from json_loader import json_load
#     return json_load('streamlit_data_ppl.json')
#     with open('streamlit_data_ppl.json','r') as fr:
#         data=eval(fr.read().replace("'",'"')) comment
#         return data
ret_dic=get_ret_dic()

# charges_dic=requests.get(charges_url).json()
botNameDic={"orb":"ORB","rsi":"RSI","it":"Intraday Trend","sh":"StopHunt","grb":"GRB","orb2pm":"ORB2pm","pcr":"NiftyOptionSelling","lapp":"Learnapp","bss":"BNF Straddle","nss":"Nifty Straddle","bos":"BNFOptionSelling","grbo":"GRB Options","bssr":"BNF Strangle","mlb":"ML Bot","bnfmon":"BNF ORB","mss":"1% Short Straddle (BNF)","mssn":"1% Short Straddle(NF)","dts":"Double Top","ats":"Auto Strangle","dbss":"BNF Straddle(Directional)"}
botCapitalDic={"orb":50000,"rsi":50000,"it":50000,"sh":50000,"grb":300000,"orb2pm":300000,"pcr":300000,"lapp":300000,"bss":300000,"nss":300000,"bos":300000,"grbo":150000,"bssr":300000,"bnfmon":150000,"mlb":400000,"mss":300000,"mssn":300000,"dts":150000,"ats":300000,"dbss":150000}
curBots=['bss','orb','rsi','it','grb','grbo','bssr','bnfmon','mlb','mss','mssn','ats','dbss']
basket_bots=['banknifty_bskt','finnifty_bskt','nifty_bskt']
curBots+=basket_bots
for bskt in basket_bots:
    botNameDic[bskt]=bskt.upper()
    botCapitalDic[bskt]=300000
botName = query_params["bot"][0] if "bot" in query_params else None



# if botName not in botsList:
#     botName='bss'
# botsList.remove('bss')
# botsList=['bss']+botsList
# if not botName:
#     botName = st.selectbox('Select a Strategy',tuple(botsList))

title_text="<h1 style='text-align: center; color: rgb(21, 86, 112);'>**♟**SQUAREOFF BOTS PERFORMANCE**♟**</h1>"
st.markdown(title_text, unsafe_allow_html=True)
if not botName:   
    botName=st.selectbox('Strategy',curBots,index=0)
botCapital,capital_used_appendum,results_row,t_stats_Df,month_groups,strat_df,drawdown_df,i_fields,botFullName=ret_dic[botName]
# with open('strat_df.txt','w') as fw:
#     fw.write(strat_df)
def df_from_string(str):
    jstr=eval(str.replace('nan','0'))
    df=pd.DataFrame.from_dict(jstr)    
    return df

t_stats_Df=df_from_string(t_stats_Df)


month_groups=df_from_string(month_groups)
strat_df=df_from_string(strat_df)
drawdown_df=df_from_string(drawdown_df)
results_row=results_row.replace('nan','0')
results_row=eval(results_row)



title_text2="<div style='text-align: center; color: rgb(21, 86, 112);'>**LIVE PERFORMANCE OF "+botFullName+"****[Capital used is "+str(botCapital)+capital_used_appendum+"]** </div>"

st.markdown(title_text2, unsafe_allow_html=True)

fig=px.line(strat_df, x="Time", y='cum_pnl', title=botFullName+' PNL',width=800, height=400)
dd_fig=px.line(drawdown_df,x="Time",y="drawdown", title=botFullName+' PNL',width=800, height=400)

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

# strat_df['Date']=strat_df.index
# strat_df['pd_date']=pd.to_datetime(strat_df['Date'],format='%Y-%m-%d')
# strat_df.sort_values('pd_date',inplace=True)
# strat_df.sort_index(key=lambda x:datetime.strptime(x,'%Y-%m-%d'),inplace=True)
# strat_df.drop('pd_date',axis=1,inplace=True)
# strat_df.to_csv(f"{botName}.csv")


