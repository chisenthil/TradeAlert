import requests
import json
import pandas as pd
import xlwings as xw
from time import sleep
from datetime import datetime,time,timedelta
import os
import numpy as np
import traceback
from Notifications import Alert
from PrepareAlertObj import PrepareAlertObj
from IndiaVIX import IndiaVIX




pd.set_option('display.width',1500)
pd.set_option('display.max_columns',75)
pd.set_option('display.max_rows',1500)

url="https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {"user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36",
           "accept-language": "en-US,en;q=0.9",
           "accept-encoding": "gzip, deflate, br"
           }


excel_file ="Option_Chain_Analysis.xlsx"
wb = xw.Book(excel_file)
sheet_oi_single = wb.sheets("OIData")
sht_live = wb.sheets("Data")
dashBoard = wb.sheets("Dashboard")
trades_sheet = wb.sheets("Trades")

trades_cur_max_pain_Cl = 7
trades_sellPutLtp_Cl = 11
trades_sellCallLtp_Cl = 18
trades_buyPutLtp_Cl = 15
trades_buyCallLtp_Cl = 22
header_rows = 1
data_rows = 3
alert_scope = ['EMAIL1' , 'GOOGLE_CALENDAR1', 'SLACK']
day_open_underlying = float(0)
new_india_vix = float(0)
day_first_vix_flag = False




require_cols = ['Trade Name','Status','Org Max Pain','Underlying','Expiry Date','Profit','Hedge Date','PE SELL Strike','PE SELL Org Price','PE SELL Crnt Price','PE SELL Alert','PE BUY Strike','PE BUY Org Price','PE BUY Crnt Price','CE SELL Strike','CE SELL Org Price','CE SELL Crnt Price','CE SELL Alert','CE BUY Strike','CE BUY Org Price','CE BUY Crnt Price']
trade_require_rows = ['Completed','Adjustment']





df_list = []
mp_list = []

oi_filename = os.path.join("Files", "oi_data_records_{0}.json".format(datetime.now().strftime("%d%m%y")))
mp_filename = os.path.join("Files", "mp_data_records_{0}.json".format(datetime.now().strftime("%d%m%y")))

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

def fetch_oi(df,mp_df):
    tries = 1
    max_retries = 1
    trade_values = pd.DataFrame()
    while tries <= max_retries:
        try:
            r = requests.get(url,headers=headers).json()
            trades_df = pd.read_excel(excel_file, sheet_name='Trades', header=header_rows, usecols=require_cols, dtype={})
            indexNames = trades_df[trades_df['Status'].isin(trade_require_rows)].index
            trades_df.drop(indexNames, inplace=True)
            alertMessage = "Job run at {0}".format(datetime.now().strftime("%H:%M"))
            print(alertMessage)
            indiaVIX = IndiaVIX()
            indiaVIX.getIndiaVIX()
            new_india_vix = indiaVIX.india_vix
            print("India VIX :{0}".format(new_india_vix))
            global day_first_vix_flag
            if time(13, 5) <= datetime.now().time() <= time(13, 20):
                day_first_vix_flag = False

            alertMsgList = [alertMessage]
            resetFlagList = []

            for ind in trades_df.index:
                prepareAlertObj = PrepareAlertObj()
                expiry = trades_df['Expiry Date'][ind].strftime("%d-%b-%Y")
                hedgeExpiryDate = trades_df['Hedge Date'][ind].strftime("%d-%b-%Y")
                prepareAlertObj.trade_name = trades_df['Trade Name'][ind]
                prepareAlertObj.old_max_pain = trades_df['Org Max Pain'][ind]
                prepareAlertObj.india_vix_flag = day_first_vix_flag
                prepareAlertObj.new_india_vix = new_india_vix

                prepareAlertObj.old_put_sell_premium = trades_df['PE SELL Org Price'][ind]
                prepareAlertObj.old_put_buy_premium = trades_df['PE BUY Org Price'][ind]
                prepareAlertObj.old_call_sell_premium = trades_df['CE SELL Org Price'][ind]
                prepareAlertObj.old_call_buy_premium = trades_df['CE BUY Org Price'][ind]

                sellPutStrike = int(trades_df['PE SELL Strike'][ind])
                buyPutStrike = int(trades_df['PE BUY Strike'][ind])
                sellCallStrike = int(trades_df['CE SELL Strike'][ind])
                buyCallStrike = int(trades_df['CE BUY Strike'][ind])

                ce_values = [data['CE'] for data in r['records']['data'] if "CE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
                pe_values = [data['PE'] for data in r['records']['data'] if "PE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]

                ce_strikes_SELL = [data['CE'] for data in r['records']['data'] if "CE" in data and (str(data['expiryDate']).lower() == str(expiry).lower() and str(data['strikePrice']).lower() == str(sellCallStrike).lower())]
                ce_strikes_BUY  = [data['CE'] for data in r['records']['data'] if "CE" in data and (str(data['expiryDate']).lower() == str(hedgeExpiryDate).lower() and str(data['strikePrice']).lower() == str(buyCallStrike).lower())]
                pe_strikes_SELL = [data['PE'] for data in r['records']['data'] if "PE" in data and (str(data['expiryDate']).lower() == str(expiry).lower() and str(data['strikePrice']).lower() == str(sellPutStrike).lower())]
                pe_strikes_BUY  = [data['PE'] for data in r['records']['data'] if "PE" in data and (str(data['expiryDate']).lower() == str(hedgeExpiryDate).lower() and str(data['strikePrice']).lower() == str(buyPutStrike).lower())]

                ce_data=pd.DataFrame(ce_values)
                pe_data=pd.DataFrame(pe_values)

                ce_data = ce_data.sort_values(['strikePrice'])
                pe_data = pe_data.sort_values(['strikePrice'])
                sheet_oi_single.range("A2").options(index=False, header=False).value = ce_data.drop(['askPrice','askQty','bidQty','bidprice','expiryDate','identifier','totalBuyQuantity','totalSellQuantity','totalTradedVolume','underlying','underlyingValue'],axis=1)[['openInterest','changeinOpenInterest','pchangeinOpenInterest','impliedVolatility','lastPrice','change','pChange','strikePrice']]
                sheet_oi_single.range("I2").options(index=False, header=False).value = pe_data.drop(['askPrice', 'askQty', 'bidQty', 'bidprice', 'expiryDate','identifier', 'totalBuyQuantity', 'totalSellQuantity','totalTradedVolume', 'underlying', 'underlyingValue', 'strikePrice'], axis=1)[['openInterest', 'changeinOpenInterest', 'pchangeinOpenInterest', 'impliedVolatility', 'lastPrice','change', 'pChange']]
                wb.api.RefreshAll()
                ce_data['type'] = "CE"
                pe_data['type'] = "PE"
                df1 = pd.concat([ce_data,pe_data])

                ce_strikes_SELL_df = pd.DataFrame(ce_strikes_SELL)
                ce_strikes_BUY_df = pd.DataFrame(ce_strikes_BUY)
                pe_strikes_SELL_df = pd.DataFrame(pe_strikes_SELL)
                pe_strikes_BUY_df = pd.DataFrame(pe_strikes_BUY)

                prepareAlertObj.new_put_sell_premium = pe_strikes_SELL_df['lastPrice'].values[0]
                prepareAlertObj.new_put_buy_premium = pe_strikes_BUY_df['lastPrice'].values[0]
                prepareAlertObj.new_call_sell_premium = ce_strikes_SELL_df['lastPrice'].values[0]
                prepareAlertObj.new_call_buy_premium = ce_strikes_BUY_df['lastPrice'].values[0]
                prepareAlertObj.new_max_pain = wb.sheets("Dashboard").range("C8").value

                trades_sheet.range((data_rows + ind, trades_sellPutLtp_Cl)).value = prepareAlertObj.new_put_sell_premium
                trades_sheet.range((data_rows + ind, trades_sellCallLtp_Cl)).value = prepareAlertObj.new_call_sell_premium
                trades_sheet.range((data_rows + ind, trades_buyPutLtp_Cl)).value = prepareAlertObj.new_put_buy_premium
                trades_sheet.range((data_rows + ind, trades_buyCallLtp_Cl)).value = prepareAlertObj.new_call_buy_premium
                trades_sheet.range((data_rows + ind, trades_cur_max_pain_Cl)).value = prepareAlertObj.new_max_pain

                pcr = pe_data['totalTradedVolume'].sum()/ce_data['totalTradedVolume'].sum()

                if time(13, 15) <= datetime.now().time() <= time(13, 59):
                    global day_open_underlying
                    day_open_underlying = df1['underlyingValue'].iloc[-1]

                prepareAlertObj.old_underlying = day_open_underlying
                prepareAlertObj.new_underlying = df1['underlyingValue'].iloc[-1]

                mp_dict = {'underlying' : float(prepareAlertObj.new_underlying),
                                                              'MaxPain': prepareAlertObj.new_max_pain,
                                                              'pcr' : pcr,
                                                              'SellPutPrice': float(prepareAlertObj.new_put_sell_premium),
                                                              'SellCallPrice': float(prepareAlertObj.new_call_sell_premium),
                                                              'BuyPutPrice': float(prepareAlertObj.new_put_buy_premium),
                                                              'BuyCallPrice': float(prepareAlertObj.new_call_buy_premium),
                                                              'Profit': float(prepareAlertObj.profit),
                                                              'Date': datetime.now().strftime("%Y-%m-%d"),
                                                              'Time': datetime.now().strftime("%H:%M"),
                                                              'TradeName': str(prepareAlertObj.trade_name),
                                                              'call_decay' : ce_data.nlargest(5,'openInterest', keep='last')['change'].mean(),
                                                              'put_decay': pe_data.nlargest(5,'openInterest', keep='last')['change'].mean()
                                                              }
                df3 = pd.DataFrame(mp_dict, index=[0])
                mp_df = pd.concat([mp_df,df3], ignore_index=True)
                mp_df = mp_df.sort_values(['TradeName','Date','Time'])
                prepareAlertObj.prepareAlert(alertMsgList,resetFlagList)
            wb.sheets['MPData'].range("A2").options(header=False).value = mp_df[['TradeName','Date','Time','MaxPain','Profit','SellCallPrice','SellPutPrice','BuyCallPrice','BuyPutPrice','pcr','call_decay','put_decay','underlying']]
            with open(mp_filename, "w") as files:
                files.write(json.dumps(mp_df.to_dict(), indent=4, sort_keys=True))
                print("Wrote JSO")
            if len(alertMsgList) > 1:
                if 'RESET_UNDERLYING' in resetFlagList:
                    day_open_underlying = prepareAlertObj.new_underlying
                if 'RESET_INDIA_VIX' in resetFlagList:
                    day_first_vix_flag = True
                alert = Alert()
                alertMessage = " ".join(str(x)+'\n' for x in alertMsgList)
                alert.sendAlert(alertMessage,alert_scope)


            return df,mp_df
        except Exception as error:
            traceback.print_exc()
            print("Error {0}".format(error))
            tries += 1
            sleep(10)
            continue
    if tries >= max_retries:
        print("Max retries exceeded. No new data at time {0}".format(datetime.now()))
        return df,mp_df


def main():
    global df_list
    df = pd.DataFrame()

    try:
        mp_list = json.loads(open(mp_filename).read())
        mp_df = pd.DataFrame().from_dict(mp_list)
    except Exception as error:
        print("Error reading data. Error : {0}".format(error))
        mp_list = []
        mp_df = pd.DataFrame()
    timeframe = 2
    while time(9,15) <= datetime.now().time() <= time(23,50):
        timenow = datetime.now()
        check = True if timenow.minute/timeframe in list(np.arange(0.0, 30.0)) else False
        if check:
            nextscan = timenow + timedelta(minutes= timeframe)
            df,mp_df = fetch_oi(df,mp_df)
            if not mp_df.empty:
                wb.api.RefreshAll()
                waitsecs = int((nextscan - datetime.now()).seconds)
                print("Wait For {0} seconds".format(waitsecs))
                sleep(waitsecs) if waitsecs > 0 else sleep(0)
            else:
                print("No Data Received")
                sleep(30)


if __name__ == '__main__':
    main()