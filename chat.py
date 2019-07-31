import logging
import sys
import getpass
from optparse import OptionParser
import sleekxmpp
from sleekxmpp.exceptions import *

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class Cliente(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("message", self.message)
        self.add_event_handler("register", self.register, threaded=True)

    def start(self, event):
        print('nani')
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            print(msg['from'])
            print(msg['body'])

    def register(self, iq):
        print('nani2')
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        print(resp)
        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()

    def get_friends(self):
        listaamigos = self.client_roster
        print(listaamigos)

    def send_files(self,jid,receiver, filename):

        stream = self['xep_0047'].open_stream(receiver)

        with open(filename) as f:
            data = f.read()
            stream.sendall(data)

    def delete_account(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.user
        resp['register'] = ' '
        resp['register']['remove'] = ' '
        print(resp)
        try:
            resp.send(now=True)
            logging.info("Account deleted for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                          e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


if __name__ == '__main__':
    optp = OptionParser()

    # JID and password options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--receiver", dest="receiver",
                    help="JID to use")
    optp.add_option("-f", "--file", dest="filename",
                    help="JID to use")
    opts, args = optp.parse_args()
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')

    print('1. Register')
    print('2. Login')
    login_client = raw_input('->')

    opts.jid = raw_input("Username: ")
    opts.password = getpass.getpass("Password: ")

    xmpp = Cliente(opts.jid, opts.password,)
    if login_client == str(2):
        xmpp.del_event_handler("register", xmpp.register)

    xmpp.register_plugin('xep_0030')
    xmpp.register_plugin('xep_0004')
    xmpp.register_plugin('xep_0060')
    xmpp.register_plugin('xep_0199')
    xmpp.register_plugin('xep_0077')
    xmpp.register_plugin('xep_0047')
    xmpp['xep_0077'].force_registration = True
    xmpp['feature_mechanisms'].unencrypted_plain = True

    if xmpp.connect(('alumchat.xyz', 5222)):
        xmpp.process(block=False)
        while True:
            print('1. Close Session')
            print('2. Delete Account')
            print('3. Send Private Message')
            print('4. Send Friend Request')
            print('5. Show Friends')
            input_client = raw_input('->')

            if input_client == str(1):
                print('...Disconnecting...')
                xmpp.disconnect()
                print('Disconnected')
                break
            if input_client == str(2):
                xmpp.delete_account()
                xmpp.disconnect()
                break
            if input_client == str(3):
                mto1 = raw_input('To: ')
                mbody1 = raw_input('->')
                xmpp.send_message(mto=mto1, mbody=mbody1, mtype='chat')
            if input_client == str(4):
                usuario = raw_input('Add User: ')
                xmpp.send_presence_subscription(pto=usuario,
                                                ptype='subscribe')
            if input_client == str(5):
                xmpp.get_friends()

            if input_client == str(6):
                opts.receiver = raw_input("Receiver: ")
                opts.filename = raw_input("File path: ")

                xmpp.send_files(opts.jid,opts.receiver, opts.filename)

    xmpp.process()
