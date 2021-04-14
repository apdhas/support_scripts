import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
import requests

bug_queues = ["vcsa-appl-mgmt-guru", "vcsa-photon",
              "vcsa-backuprestore-guru", "vcsa-deployment-guru",
              "vcsa-logsupport-guru", "vcsa-patching-guru", "vmon-guru",
              "net-dumper-guru", "tls-reconfiguration-guru",
              "vcsa-appl-mon-guru"]

status = ["new", "assigned", "reopened"]
bccList = ["mathanv@vmware.com", "mkumar7@vmware.com", "dhasa@vmware.com",
           "sk4@vmware.com", "vtk@vmware.com", "sreddyvelaga@vmware.com",
           "swapnily@vmware.com", "pranganath@vmware.com",
           "kulkarniraje@vmware.com", "nd@vmware.com", "afsalp@vmware.com",
           "shampawarh@vmware.com", "grevathi@vmware.com",
           "bgangadhars@vmware.com"]

body = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <style type="text/css">
      table {
        background: white;
        border-radius:3px;
        border-collapse: collapse;
        height: auto;
        max-width: 900px;
        padding:5px;
        width: 100%;
        animation: float 5s infinite;
      }
      th {
        color:#D5DDE5;;
        background:#1b1e24;
        border-bottom: 4px solid #9ea7af;
        font-size:14px;
        font-weight: 300;
        padding:10px;
        text-align:center;
        vertical-align:middle;
      }
      tr {
        border-top: 1px solid #C1C3D1;
        border-bottom: 1px solid #C1C3D1;
        border-left: 1px solid #C1C3D1;
        color:#666B85;
        font-size:16px;
        font-weight:normal;
      }
      tr:hover td {
        background:#4E5066;
        color:#FFFFFF;
        border-top: 1px solid #22262e;
      }
      td {
        background:#FFFFFF;
        padding:10px;
        text-align:left;
        vertical-align:middle;
        font-weight:300;
        font-size:13px;
        border-right: 1px solid #C1C3D1;
      }
    </style>
  </head>
  <body>
    Dear all,<br> <br>
    Please find the list of bugs in queue for this week.<br><br>
    <table>
      <thead>
        <tr style="border: 1px solid #1b1e24;">
          <th>Bug_Id</th>
          <th>Priority</th>
          <th>Severity</th>
          <th>Summary</th>
          <th>Created On</th>
          <th>Last Update</th>
        </tr>
      </thead>
      <tbody>
      TABLE_BODY
      </tbody>
    </table>
    <br>
    VCSA CODB Queue Owner of the week:
    <a href='mailto:kulkarniraje@vmware.com'>mkumar7@vmware.com</a>.
    <br> <br>
    For more assistance please contact:
    <a href='mailto:dhasa@vmware.com'>dhasa@vmware.com</a>,
    <a href='mailto:sk4@vmware.com'>sk4@vmware.com</a>.<br> <br>
    Thank you!
  </body>
</html>
"""

tablebody = """
        <tr>
          <td><a href="https://bugzilla.eng.vmware.com/show_bug.cgi?id=ID">ID
          </a></td>
          <td>PRIORITY</td>
          <td>SEVERITY</td>
          <td>SUMMARY</td>
          <td>CREATED</td>
          <td>CHANGED</td>
        </tr>
"""


def getAllBugs():
    bugs = []
    data = {"username": "svc.vcsa-blr", "password": "^VHB^C7^zwpcv2.475!"}
    response = requests.post(
        "https://bugzilla-rest.eng.vmware.com/rest/v1/token",
        json.dumps(data))
    rep = json.loads(response.text)
    weekday = datetime.datetime.now().weekday()
    if weekday >= 0 and weekday < 5:
        weekday = weekday + 3
    accessToken = rep["accesstoken"]
    for queue in bug_queues:
        for stat in status:
            r = requests.get(
                "https://bugzilla-rest.eng.vmware.com/rest/v1/bug/query"
                "?assignee=" + queue + "&status=" + stat +
                "&lastChangeDays=" + str(weekday) +
                "&creationDays=" + str(weekday),
                headers={'Authorization': 'Bearer ' + accessToken})

            resp = json.loads(r.text)
            if "bugs" in resp:
                for bug in resp["bugs"]:
                    bugs.append(bug)
    return bugs


def createMsg():
    table_rows = []
    bugs = getAllBugs()
    for bug in bugs:
        if "ToT" not in bug["summary"]:
            table_row = tablebody.replace("ID", str(bug["id"])).replace(
                "PRIORITY", bug["priority"]).replace(
                "SEVERITY", bug["severity"]).replace(
                "SUMMARY", bug["summary"]).replace(
                "CREATED", bug["created_ts"]).replace(
                "CHANGED", bug["delta_ts"])
            table_rows.append(table_row)
    if table_rows:
        HTML = body.replace("TABLE_BODY", '\n'.join(table_rows))
        message = MIMEMultipart("alternative", None, [MIMEText(HTML, 'html')])
        return message
    else:
        return None


def SendEmail(fromaddr, toaddrs, bccList, subject, body,
              throw_exception=False):
    try:
        # make toaddrs unique
        smtp = smtplib.SMTP('smtp.vmware.com')
        message = MIMEMultipart("alternative")
        message["Subject"] = "VCSA CODB Bugs"
        message["From"] = fromaddr
        message["To"] = toaddrs
        msg = createMsg()
        if not msg:
            print("No bugs in queue")
            return
        message.attach(msg)
        smtp.sendmail(fromaddr, [toaddrs] + bccList, message.as_string())
    except smtplib.SMTPRecipientsRefused as e:
        # if recipient is not valid, then send to a known valid email address
        bad_addr_msg = 'Unable to send email to original list of ' \
                       'recipients.  These recipient email address(es)' \
                       ' were refused: %s\r\n\r\n' % toaddrs
        bad_addr_msg += 'The original email is shown below:\r\n'
        body.insert(0, bad_addr_msg)
        toaddrs = ["dhasa@vmware.com", ]
        SendEmail(fromaddr, toaddrs, [], subject, body)
        if throw_exception:
            raise e
    except Exception as e:
        if throw_exception:
            raise e


SendEmail("vcsa-codb@vmware.com", "kulkarniraje@vmware.com",
          bccList,
          "Test message",
          "", True)
