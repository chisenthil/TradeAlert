import smtplib
import ssl

class EmailAlert():
    port = 587  # For SSL
    smtp_server = "smtp.mail.yahoo.com"
    sender_email = "chisenthil@yahoo.com"  # Enter your address
    receiver_email = "chisenthil@yahoo.com"  # Enter receiver address
    password = "Nothing02*"
    message = """\
    Subject: Hi there

    This message is sent from Python."""

    def __init__(self):
        pass

    def sendEmailAlert(self, message):
        self.__send_email(message)

    def __send_email(self, message):
        context = ssl.create_default_context()
        with smtplib.SMTP(Alert.smtp_server, Alert.port) as server:
            # server.ehlo()  # Can be omitted
            server.starttls(context=context)
            # server.ehlo()  # Can be omitted
            server.login(Alert.sender_email, Alert.password)
            server.sendmail(Alert.sender_email, Alert.receiver_email, message)
            server.quit()