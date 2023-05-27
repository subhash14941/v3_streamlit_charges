import pandas as pd
from json_loader import *
import re



def calCulateReturn(pnl,cap):
  
    try:
        fc=float(cap)
        fp=float(pnl)
    except ValueError:
        return 0
    if(not re.search('\d',str(pnl)) or not re.search('\d',str(cap))):
        return 0 
    
    
    elif (fc==0 or fp==0):
        return 0
    else:
        return 100*float(pnl)/float(cap)

def agg_df(pnlDf,capDf):
    returnsColumns=[c+' Returns' for c in capDf.columns]
    capDf.columns=[c+' Capital' for c in capDf.columns]
    pnlDf.columns=[c+' PnL' for c in pnlDf.columns]

    result = pd.concat([capDf, pnlDf], axis=1, join="inner")



    for r in returnsColumns:
        stratName=r.split(' Returns')[0];
        capColumnName=stratName+' Capital'
        pnlColumnName=stratName+' PnL'
        result[r]=result.apply(lambda x:calCulateReturn(x[pnlColumnName],x[capColumnName]),axis=1)
    return result

