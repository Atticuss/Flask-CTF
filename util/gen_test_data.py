import hashlib, string, base64
from random import randrange

fnames = []
with open('first_names.txt', 'r') as f:
    for l in f:
        fnames.append(l.strip())

lnames = []
with open('last_names.txt', 'r') as f:
    for l in f:
        lnames.append(l.strip())

with open('users.txt', 'w') as f:
    charset = string.ascii_letters + string.digits
    for i in range(100):
        fname = fnames[randrange(len(fnames))]
        lname = lnames[randrange(len(lnames))]
        uname = ('%s_%s' % (fname[0], lname)).lower()

        pw = ''
        for i in range(15):
            pw += charset[randrange(len(charset))]
        
        m = hashlib.sha1()
        m.update(pw.encode())
        hashed_pw = base64.b64encode(m.digest()).decode()
        
        account_balance = randrange(100000)

        if i == 99:
            f.write('%s\t%s\t%s\t%s\t%s' % (fname, lname, account_balance, uname, hashed_pw))
        else:
            f.write('%s\t%s\t%s\t%s\t%s\n' % (fname, lname, account_balance, uname, hashed_pw))

