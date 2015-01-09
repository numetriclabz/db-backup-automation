import os
import datetime
import tinys3
import sendgrid
import MySQLdb
import hashlib
from time import gmtime, strftime

date = strftime("%Y-%m-%d", gmtime())

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

def sendMail(what,status):
        sg = sendgrid.SendGridClient('sendgrid_user', 'sendgrid_password')

        message = sendgrid.Mail()
        message.add_to('Someone <some@someone.com>')
        message.add_bcc('other@otherone.com')
        message.set_subject('Database_Name database dumped : {what}'.format(what=status))
        message.set_html('Database_Name database dumped to s3 bucket.\n FileName : {what}'.format(what=what))
        message.set_text('Body')
        message.set_from('Sender Name<sender@email.com>')
        status, msg = sg.send(message)

host='hostname'
user='db_username'
passwd='db_password'
db='database_name'
now = datetime.datetime.now()

filename = "backup_" + db + now.strftime("%Y-%m-%d_%H:%M") + ".zip"
sql_filename = "backup_" + db + now.strftime("%Y-%m-%d_%H:%M") + ".sql"

os.popen("mysqldump -u {user} -p{password} -h {host} -e --opt -c {database} > {filename}".format(user=user,password=passwd,host=host,database=db,filename=sql_filename))

os.popen("zip {filename} {sql_filename}".format(filename=filename,sql_filename=sql_filename))

S3_ACCESS_KEY = "aws_access_key"
S3_SECRET_KEY = "aws_secret_key"
bucketName = "bucket_name"
Passphrase = "aws_passphrase"

conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,tls=True)
f = open(filename,'rb')
conn.upload(filename,f,bucketName)
filemd5 = md5Checksum(filename)
f = open('md5'+date+'.txt','w')
f.write(filemd5)
f.close()

fname = "md5"+date+".txt"
with open(fname) as f:
    content = f.readlines()
print content
firstMd5 = content[0]
os.popen("rm {filename}".format(filename=filename))
os.popen("rm {filename}".format(filename=sql_filename))

os.popen("s3cmd get s3://{bucket}/{file}".format(file=filename,bucket=bucketName))
lastMd5 = md5Checksum(filename)
if(firstMd5 == lastMd5):
    success = "success"
    sendMail(filename, success)
else:
    fail = "failure in encryption"
    sendMail(filename, fail)

os.popen("rm md5*")
os.popen("rm {filename}".format(filename=filename))
print "Done"


