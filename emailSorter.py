import sys
from imapclient import IMAPClient

def fetchMessages(server, maxEmail):
    print('Fetching messages...')
    getIds = []
    msgs = []
    emailIds = server.search([b'NOT', b'DELETED'])

    # Counting down maxEmail number of ids
    startIndex = len(emailIds)-maxEmail
    i = 0
    for id in emailIds:
        if(i >= startIndex):
            getIds.append(id)
        i += 1

    # Fetching the selected emails
    rawMsgs = server.fetch(getIds, ['ENVELOPE', 'RFC822.SIZE'])

    # Making a list from the emails
    for key, value in rawMsgs.items():
        msgs.append(value)
    print('Fetching is done!')
    return msgs

def getMyInfo(Msgs):
    myInfos = []
    for msg in Msgs:
        mailbox = msg[b'ENVELOPE'].from_[0].mailbox
        host = msg[b'ENVELOPE'].from_[0].host
        info = {'from': mailbox+b'@'+host, 'size': msg[b'RFC822.SIZE']}
        myInfos.append(info)
    return myInfos

Host = "imap.gmail.com"
UserEmail = ""
UserPwd = ""
numberOfEmails = 0

for arg in sys.argv:
    if((len(arg) > 3) and (arg[0] == '-') and (arg[2] == '=')):
        if(arg[1] == 'u'):
            UserEmail = arg[3:]
        elif(arg[1] == 'p'):
            UserPwd = arg[3:]
        elif(arg[1] == 'n'):
            numberOfEmails = int(arg[3:])

if((len(UserEmail) != 0) and (len(UserPwd) != 0) and (numberOfEmails != 0)):
    server = IMAPClient(Host, use_uid=True, ssl=True)
    server.login(UserEmail, UserPwd)
    select_info = server.select_folder("INBOX")

    allMessages = fetchMessages(server, numberOfEmails)
    allMyInfo = getMyInfo(allMessages)

    groupedSenders = []

    for myInfo in allMyInfo:
        i = 0
        while((i < len(groupedSenders)) and (groupedSenders[i]['from'] != myInfo['from'])):
            i += 1
        if(i == len(groupedSenders)):
            groupedSenders.append({'from': myInfo['from'], 'amount': 1, 'size': myInfo['size']})
        else:
            groupedSenders[i]['amount'] += 1
            groupedSenders[i]['size'] += myInfo['size']

    allSize = 0
    for i in range(0, len(groupedSenders)):
        max = 0
        maxIndex = 0
        for j in range(i, len(groupedSenders)):
            if(groupedSenders[j]['amount'] > max):
                max = groupedSenders[j]['amount']
                maxIndex = j
        temp = groupedSenders[i]
        groupedSenders[i] = groupedSenders[maxIndex]
        groupedSenders[maxIndex] = temp
        allSize += groupedSenders[i]['size']

    outputStr = "Result:\n"
    outputStr += 'All: '+str(len(allMyInfo))+'pcs\n'
    outputStr += 'All size: '+str(round(allSize/1024/1024, 4)) + ' MB\n'
    for sender in groupedSenders:
        outputStr += str(round(100*sender['amount']/len(allMyInfo), 2)) + '%\t'
        outputStr += str(sender['amount'])+'pcs\t'
        outputStr += str(round(sender['size']/1024, 2))+' kB\t'
        outputStr += str(sender['from'], 'utf-8') + '\n'

    print(outputStr)