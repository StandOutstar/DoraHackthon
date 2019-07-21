from neorpc.Client import RPCClient
client = RPCClient()
blockchain_height = client.get_height()
print(blockchain_height)
balance = client.get_balance("602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7")
print(balance)