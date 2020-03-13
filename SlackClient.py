from slacker import Slacker


class SlackClient():
    slack_token = "xoxb-978886491190-963905091170-WryyugXsiecjWeG8l6EXEVn4"

    def __init__(self):
        pass

    def sendMessageToSlack(self, message):
        self.__send_slack_alert(message)

    def __send_slack_alert(self, message):
        slack = Slacker(SlackClient.slack_token)
        slack.chat.post_message('#learn', message)