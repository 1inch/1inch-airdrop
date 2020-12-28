from collections import namedtuple
from enum import Enum


class Operation(Enum):
    ADDITION = 1
    REMOVAL = 2


LPTransfer = namedtuple('LPTransfer', ['timestamp', 'pool', 'addr_from', 'addr_to', 'amount'])
TokenTransfer = namedtuple('TokenTransfer', ['timestamp', 'pool', 'token', 'operation', 'amount'])
Price = namedtuple('Price', ['timestamp', 'price'])
InchTxn = namedtuple('InchTxn', ['project', 'tx_from', 'to_token', 'from_token', 'to_amount', 'from_amount', 'tx_hash',
                                 'block_time', 'from_usd', 'to_usd'])
Prices = namedtuple('Prices', ['usdc_prices', 'usdt_prices', 'dai_prices', 'eth_prices'])
