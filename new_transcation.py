import binascii
import hashlib
from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neo.Core.TX.Transaction import ContractTransaction, TransactionOutput
from neo.Core.TX.InvocationTransaction import InvocationTransaction
from neo.Core.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from neo.Core.CoinReference import CoinReference
from neo.SmartContract.ContractParameterContext import ContractParametersContext
from neocore.Fixed8 import Fixed8
from neocore.UInt256 import UInt256
from neocore.UInt160 import UInt160
from neocore.KeyPair import KeyPair
from neo import Blockchain
from base58 import b58decode
from neo.VM.ScriptBuilder import ScriptBuilder
from neo.Wallets.utils import to_aes_key


def newTransacation(addr1,addr2,amount):
    neo_asset_id = Blockchain.GetSystemShare().Hash
    gas_asset_id = Blockchain.GetSystemCoin().Hash

    source_address = addr1
    source_script_hash = address_to_scripthash(source_address)

    destination_address = addr2
    destination_script_hash = address_to_scripthash(destination_address)

    # Let's start with building a ContractTransaction
    # The constructor already sets the correct `Type` and `Version` fields, so we do not have to worry about that
    contract_tx = ContractTransaction()

    # Since we are building a raw transaction, we will add the raw_tx flag

    contract_tx.raw_tx = True

    # Next we can add Attributes if we want. Again the various types are described in point 4. of the main link above
    # We will add a simple "description"
    contract_tx.Attributes.append(TransactionAttribute(usage=TransactionAttributeUsage.Description,
                                                       data="My raw contract transaction description"))

    # The next field we will set are the inputs. The inputs neo-python expects are of the type ``CoinReference``
    # To create these inputs we will need the usual `PrevHash` and `PrevIndex` values.
    # You can get the required data by using e.g. the neoscan.io API: https://api.neoscan.io/docs/index.html#api-v1-get-3
    # The `PrevHash` field equals to neoscan's `balance.unspent[index].txid` key, and `PrevIndex` comes from `balance.unspent[index].n`
    # It is up to the transaction creator to make sure that the sum of all input ``value`` fields is equal to or bigger than the amount that's intended to be send
    # The below values are taken from data out of the `neo-test1-w.wallet` fixture wallet (a wallet neo-python uses for internal testing)
    input1 = CoinReference(
        prev_hash=UInt256(data=binascii.unhexlify('949354ea0a8b57dfee1e257a1aedd1e0eea2e5837de145e8da9c0f101bfccc8e')),
        prev_index=1)
    contract_tx.inputs = [input1]

    # Next we will create the outputs.
    # The above input has a value of 50. We will create 2 outputs.

    # 1 output for sending 3 NEO to a specific destination address
    send_to_destination_output = TransactionOutput(AssetId=neo_asset_id, Value=Fixed8.FromDecimal(amount),
                                                   script_hash=destination_script_hash)

    contract_tx.outputs = [send_to_destination_output]

    # at this point we've build our unsigned transaction and it's time to sign it before we get the raw output that we can send to the network via RPC
    # we need to create a Wallet instance for helping us with signing
    wallet = UserWallet.Create('path', to_aes_key('mypassword'), generate_default_key=False)

    # if you have a WIF use the following
    # this WIF comes from the `neo-test1-w.wallet` fixture wallet
    private_key = KeyPair.PrivateKeyFromWIF("Ky94Rq8rb1z8UzTthYmy1ApbZa9xsKTvQCiuGUZJZbaDJZdkvLRV")

    # if you have a NEP2 encrypted key use the following instead
    # private_key = KeyPair.PrivateKeyFromNEP2("NEP2 key string", "password string")

    # we add the key to our wallet
    wallet.CreateKey(private_key)

    # and now we're ready to sign
    context = ContractParametersContext(contract_tx)
    wallet.Sign(context)

    contract_tx.scripts = context.GetScripts()

    print(contract_tx.Hash.ToString())

    raw_tx = contract_tx.ToArray()

    return raw_tx

def address_to_scripthash(address: str) -> UInt160:
        """Just a helper method"""
        AddressVersion = 23  # fixed at this point
        data = b58decode(address)
        if len(data) != 25:
            raise ValueError('Not correct Address, wrong length.')
        if data[0] != AddressVersion:
            raise ValueError('Not correct Coin Version')

        checksum_data = data[:21]
        checksum = hashlib.sha256(hashlib.sha256(checksum_data).digest()).digest()[:4]
        if checksum != data[21:]:
            raise Exception('Address format error')
        return UInt160(data=data[1:21])
