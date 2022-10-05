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
    rawMsgs = server.fetch(getIds, ['ENVELOPE'])

    # Making a list from the emails
    for key, value in rawMsgs.items():
        msgs.append(value)
    print('Fetching is done!')
    return msgs

def getSenders(Msgs):
    senders = []
    for msg in Msgs:
        mailbox = msg[b'ENVELOPE'].from_[0].mailbox
        host = msg[b'ENVELOPE'].from_[0].host
        senders.append(mailbox+b'@'+host)
    return senders

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
    allSenders = getSenders(allMessages)

    groupedSenders = []

    for sender in allSenders:
        i = 0
        while((i < len(groupedSenders)) and (groupedSenders[i][0] != sender)):
            i += 1
        if(i == len(groupedSenders)):
            groupedSenders.append([sender, 1])
        else:
            groupedSenders[i][1] += 1

    for i in range(0, len(groupedSenders)):
        max = 0
        maxIndex = 0
        for j in range(i, len(groupedSenders)):
            if(groupedSenders[j][1] > max):
                max = groupedSenders[j][1]
                maxIndex = j
        temp = groupedSenders[i]
        groupedSenders[i] = groupedSenders[maxIndex]
        groupedSenders[maxIndex] = temp

    print('Result:')
    print('All: '+str(len(allSenders))+'pcs')
    for sender in groupedSenders:
        print(str(round(100*sender[1]/len(allSenders), 2))+'%\t', str(sender[1])+'pcs\t', str(sender[0], 'utf-8'))