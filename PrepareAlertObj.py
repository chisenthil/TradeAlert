
class PrepareAlertObj():
    trade_name = ""
    india_vix_flag = False

    old_max_pain = int(0)
    new_max_pain = int(0)

    old_underlying = float(0)
    new_underlying = float(0)

    profit = float(0)



    old_put_sell_premium = float(0)
    new_put_sell_premium = float(0)
    old_put_buy_premium = float(0)
    new_put_buy_premium = float(0)

    old_call_sell_premium = float(0)
    new_call_sell_premium = float(0)
    old_call_buy_premium = float(0)
    new_call_buy_premium = float(0)
    new_india_vix = float(0)


    def __init__(self):
        self.trade_name = ""
        self.india_vix_flag = False
        self.old_max_pain = int(0)
        self.new_max_pain = int(0)
        self.old_underlying = float(0)
        self.new_underlying = float(0)
        self.profit = float(0)

        self.old_put_sell_premium = float(0)
        self.new_put_sell_premium = float(0)
        self.old_put_buy_premium = float(0)
        self.new_put_buy_premium = float(0)

        self.old_call_sell_premium = float(0)
        self.new_call_sell_premium = float(0)
        self.old_call_buy_premium = float(0)
        self.new_call_buy_premium = float(0)
        self.new_india_vix = float(0)




    def prepareAlert(self,alertMsgList,resetFlagList):
        self.__prepare_alert(alertMsgList,resetFlagList)

    def __prepare_alert(self, alertMsgList,resetFlagList):
        self.__calculate_profit()
        print(self.trade_name + ": Underlying Moved New : " + str(self.new_underlying) + " Old :" + str(self.old_underlying) + "  Diff :" +str(self.new_underlying-self.old_underlying))

        if self.new_call_sell_premium >= (self.old_call_sell_premium*3):
            message= self.trade_name + ": Call Premium Trippled New : " + str(self.new_call_sell_premium) + " Old :" + str(self.old_call_sell_premium)
            alertMsgList.append(message)
        if self.new_put_sell_premium >= (self.old_put_sell_premium * 3):
            message = self.trade_name + ": Put Premium Trippled  New : " + str(self.new_put_sell_premium) + " Old :" + str(self.old_put_sell_premium)
            alertMsgList.append(message)
        if self.new_max_pain >= (self.old_max_pain+100) or self.new_max_pain <= (self.old_max_pain-100):
            message = self.trade_name + ": Max Pain Moved New : " + str(self.new_max_pain) + " Old :" + str(self.old_max_pain)
            alertMsgList.append(message)
        if self.new_underlying >= (self.old_underlying + 100) or self.new_underlying <= (self.old_underlying - 100):
            message = self.trade_name + ": Underlying Moved New : " + str(self.new_underlying) + " Old :" + str(self.old_underlying)
            alertMsgList.append(message)
            resetFlagList.append('RESET_UNDERLYING')
        if self.india_vix_flag == False and self.new_india_vix >= 20:
            message = self.trade_name + ": India VIX > 20  Flag : " + str(self.india_vix_flag) + " Value :" + str(self.new_india_vix)
            alertMsgList.append(message)
            resetFlagList.append('RESET_INDIA_VIX')
        return alertMsgList

    def __calculate_profit(self):
        sellPutProfit = self.old_put_sell_premium - self.new_put_sell_premium
        sellCallProfit = self.old_call_sell_premium - self.new_call_sell_premium
        buyPutProfit = self.new_put_buy_premium - self.old_put_buy_premium
        buyCallProfit = self.new_call_buy_premium - self.old_call_buy_premium
        self.profit = sellPutProfit + sellCallProfit + buyPutProfit + buyCallProfit