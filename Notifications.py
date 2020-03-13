import smtplib
import ssl
from SlackClient import SlackClient
from EmailAlert import EmailAlert

class Alert():

    def __init__(self):
        pass

    def sendAlert(self, message,alert_scope):
        if 'EMAIL' in alert_scope:
            print("Sending Email Alert")
            #self.__send_email(message)
        if 'SLACK' in alert_scope:
            self.__slack_client(message)
        if 'GOOGLE_CALENDAR' in alert_scope:
            print("Sending GOOGLE_CALENDAR Alert")



    def __send_email(self, message):
        email_alert = EmailAlert();
        email_alert.sendEmailAlert(message)

    def __slack_client(self, message):
       slack_client = SlackClient();
       slack_client.sendMessageToSlack(message)