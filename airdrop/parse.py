import csv
import datetime
import json

from airdrop.config import STOP_TIMESTAMP, START_TIMESTAMP, ZERO_ADDR
from airdrop.structs import InchTxn, LPTransfer, Price, TokenTransfer, Operation, LimitOrdersUser, UniswapUser


def get_uniswap_users():
    with open('./data/uniswap.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        return [
            UniswapUser('0x' + row[0], int(row[1]), int(row[2]))
            for row in [row for row in spamreader][1:]
        ]


def get_limit_users():
    with open('./data/limit-orders.json') as in_f:
        return [
            LimitOrdersUser('0x' + row['maker_address'], row['trades'], row['volume'], datetime.datetime.strptime(row['ts'], "%Y-%m-%dT%H:%M:%SZ").timestamp())
            for row in json.load(in_f)['query_result']['data']['rows']
            if datetime.datetime.strptime(row['ts'], "%Y-%m-%dT%H:%M:%SZ").timestamp() <= STOP_TIMESTAMP
        ]


def get_relay_trades():
    with open('./data/relays.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        rows = [
            InchTxn(row[0], '0x' + row[1], '0x' + row[2], '0x' + row[3], row[4], row[5], '0x' + row[6],
                    datetime.datetime.strptime(row[7], "%Y-%m-%dT%H:%M:%SZ"), float(row[8] if row[8] else '0'),
                    float(row[9] if row[9] else '0'))
            for row in [row for row in spamreader][1:]
        ]
    
    return [t for t in rows if t.block_time.timestamp() <= STOP_TIMESTAMP]


def get_1inch_trades(filename, filename2=None):
    rows = []
    print(filename, filename2)
    for f in [filename2, filename]:
        if f is not None:
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile)
                rows.extend([
                    InchTxn(row[0], '0x' + row[1], '0x' + row[2], '0x' + row[3], row[4], row[5], '0x' + row[6],
                            datetime.datetime.strptime(row[7], "%Y-%m-%dT%H:%M:%SZ"), float(row[8] if row[8] else '0'),
                            float(row[9] if row[9] else '0'))
                    for row in [row for row in spamreader][1:]
                ])

    inch = []
    split = []
    router = []
    mooniswap = []

    for r in rows:
        if r.project == '1inch':
            inch.append(r)
        elif r.project == '1split':
            split.append(r)
        elif r.project == '1proto':
            router.append(r)
        elif r.project == 'mooniswap':
            mooniswap.append(r)
        elif r.project == 'mooniswap2':
            mooniswap.append(r)
        else:
            raise RuntimeError("Invalid project")

    trades = inch.copy()

    used_txns = set(r.tx_hash for r in trades)

    for proj in [split, router, mooniswap]:
        for r in proj:
            if r.tx_hash not in used_txns:
                trades.append(r)
                used_txns.add(r.tx_hash)

    return [t for t in trades if t.block_time.timestamp() <= STOP_TIMESTAMP]


def get_gitcoin_users():
    with open('./data/gitcoin.json') as csvfile:
        return json.load(csvfile)['addresses']


def get_eth_transfers(pools, eth_filename):
    with open(eth_filename) as csvfile:
        spamreader = csv.reader(csvfile)
        rows = [row for row in spamreader][1:]

    eth_transfers = dict()
    for row in rows:
        if row[2] in pools:
            assert row[3] not in pools
            pool = row[2]
            operation = Operation.REMOVAL
        elif row[3] in pools:
            pool = row[3]
            operation = Operation.ADDITION
        else:
            assert False
        if pool not in eth_transfers:
            eth_transfers[pool] = []
        eth_transfers[pool].append(TokenTransfer(int(row[0]), pool, ZERO_ADDR, operation, int(row[4])))

    print('Got ETH transfers for {} pools'.format(len(eth_transfers)))

    return eth_transfers


def get_token_transfers(pools, erc_filename):
    with open(erc_filename) as csvfile:
        spamreader = csv.reader(csvfile)
        rows = [row for row in spamreader][1:]

    token_transfers = dict()
    for row in rows:
        if row[2] in pools:
            assert row[3] not in pools
            pool = row[2]
            operation = Operation.REMOVAL
        elif row[3] in pools:
            pool = row[3]
            operation = Operation.ADDITION
        else:
            assert False
        if pool not in token_transfers:
            token_transfers[pool] = []
        token_transfers[pool].append(TokenTransfer(int(row[0]), pool, row[1], operation, int(row[4], 16)))

    print('Got token transfers for {} pools'.format(len(token_transfers)))

    return token_transfers


def get_lp_transfers(lp_filename):
    with open(lp_filename) as csvfile:
        spamreader = csv.reader(csvfile)
        rows = [row for row in spamreader][1:]

    lp_transfers = dict()
    for row in rows:
        if row[1] not in lp_transfers:
            lp_transfers[row[1]] = []
        lp_transfers[row[1]].append(LPTransfer(int(row[0]), row[1], row[2], row[3], int(row[4], 16)))

    print('Got lp transfers for {} pools'.format(len(lp_transfers)))

    return lp_transfers


def get_eth_prices():
    with open('./data/eth.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        rows = [row for row in spamreader][1:]
        return [Price(int(float(row[0])), 10 ** 20 // int(float(row[1]) * 100)) for row in rows]


def get_usdc_prices():
    return [Price(START_TIMESTAMP, 10 ** 6)]


def get_usdt_prices():
    return [Price(START_TIMESTAMP, 10 ** 6)]


def get_dai_prices():
    return [Price(START_TIMESTAMP, 10 ** 18)]
