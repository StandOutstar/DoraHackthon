from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neo.Wallets.utils import to_aes_key
from neo.Settings import settings

def registerUser(username,password):
    settings.setup_privnet()
    UserWallet.Create(username+".json",to_aes_key(password))
    return UserWallet.Addresses

def getAddress(username,password):
    settings.setup_privnet()
    UserWallet.Open(username+".json",to_aes_key(password))
    address = UserWallet.Addresses[0]
    return address[0]
