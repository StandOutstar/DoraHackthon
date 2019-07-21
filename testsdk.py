from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neo.Wallets.utils import to_aes_key
from neo.Settings import settings

from register_user import registerUser, getAddress

#registerUser("tom","1234567890")
#registerUser("john","1234567890")

addr1 = getAddress("tom","1234567890")
addr2 = getAddress("john","1234567890")
print(addr1)
print(addr2)



