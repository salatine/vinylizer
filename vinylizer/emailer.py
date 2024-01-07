import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from os.path import basename

def send_email(subject, body, sender, receivers, app_password, resume_attachment_path):
    msg = MIMEMultipart() 
    msg['From'] = sender 
    msg['To'] = receivers[0]
    msg['CC'] = ', '.join(receivers[1:])
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain')) 
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(open(resume_attachment_path, 'rb').read())
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', 'attachment', filename=basename(resume_attachment_path)) 
    msg.attach(p) 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(sender, app_password)
    text = msg.as_string() 
    s.sendmail(sender, receivers, text) 
    s.quit() 
