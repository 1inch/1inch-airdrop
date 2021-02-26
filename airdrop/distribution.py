import json

from airdrop.config import FIRST_MINING_PROGRAM, SECOND_MINING_PROGRAM, FIX_REWARD, GITCOIN_REWARD, AIRDROP_PROGRAM, \
    FIRST_MINING_PROGRAM_START, SECOND_MINING_PROGRAM_START, UNISWAP_AIRDROP_PROGRAM, UNISWAP_FIX_REWARD
from airdrop.parse import get_usdc_prices, get_usdt_prices, get_dai_prices, get_eth_prices, get_lp_transfers, \
    get_eth_transfers, get_token_transfers, get_1inch_trades, get_gitcoin_users, get_limit_users, get_relay_trades, \
    get_uniswap_users
from airdrop.process import process_mining_program, get_1inch_users, get_all_users, process_uniswap_users
from airdrop.structs import Prices


def print_distribution(all_rewards, filename):
    with open(filename, 'w') as out_f:
        d = {
            k: hex(v)[2:]
            for k, v in all_rewards.items()
            if v > 0
        }
        json.dump(d, out_f)


def gen_initial_distribution():
    prices = Prices(
        usdc_prices=get_usdc_prices(),
        usdt_prices=get_usdt_prices(),
        dai_prices=get_dai_prices(),
        eth_prices=get_eth_prices(),
    )

    lp_transfers = get_lp_transfers('data/bq-lp.csv')
    pools = list(lp_transfers.keys())

    first_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth.csv'),
        get_token_transfers(pools, 'data/bq-erc20.csv'),
        prices,
        FIRST_MINING_PROGRAM,
        0
    )

    lp_transfers = get_lp_transfers('data/bq-lp-2.csv')
    pools = list(lp_transfers.keys())

    second_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth-2.csv'),
        get_token_transfers(pools, 'data/bq-erc20-2.csv'),
        prices,
        SECOND_MINING_PROGRAM,
        0
    )

    inch_trades = get_1inch_trades('./data/dune-swaps.csv')
    inch_users = get_1inch_users(inch_trades)

    gitcoin_users = get_gitcoin_users()

    fixed_rewards = {
        k: FIX_REWARD
        for k in inch_users
    }

    gitcoin_rewards = {
        k: GITCOIN_REWARD
        for k in gitcoin_users
    }

    volume_reward = AIRDROP_PROGRAM - FIX_REWARD * len(fixed_rewards) - GITCOIN_REWARD * len(gitcoin_rewards)

    total_weight = sum(s['weight'] for s in inch_users.values())

    volume_rewards = {
        k: volume_reward * s['weight'] // total_weight
        for k, s in inch_users.items()
    }

    total_rewards = {}

    for d in [fixed_rewards, gitcoin_rewards, volume_rewards, first_liq_mining_rewards, second_liq_mining_rewards]:
        for u, r in d.items():
            if u not in total_rewards:
                total_rewards[u] = 0
            total_rewards[u] += r

    return total_rewards


def gen_second_distribution():
    prices = Prices(
        usdc_prices=get_usdc_prices(),
        usdt_prices=get_usdt_prices(),
        dai_prices=get_dai_prices(),
        eth_prices=get_eth_prices(),
    )

    lp_transfers = get_lp_transfers('data/bq-lp.csv')
    pools = list(lp_transfers.keys())

    first_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth.csv'),
        get_token_transfers(pools, 'data/bq-erc20.csv'),
        prices,
        FIRST_MINING_PROGRAM,
        FIRST_MINING_PROGRAM_START
    )

    lp_transfers = get_lp_transfers('data/bq-lp-2.csv')
    pools = list(lp_transfers.keys())

    second_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth-2.csv'),
        get_token_transfers(pools, 'data/bq-erc20-2.csv'),
        prices,
        SECOND_MINING_PROGRAM,
        SECOND_MINING_PROGRAM_START
    )

    inch_trades = get_1inch_trades('./data/dune-swaps-2.csv')
    limit_users = get_limit_users()
    relay_trades = get_relay_trades()
    inch_users = get_all_users(inch_trades, limit_users, relay_trades)

    gitcoin_users = get_gitcoin_users()

    fixed_rewards = {
        k: FIX_REWARD
        for k in inch_users
    }

    gitcoin_rewards = {
        k: GITCOIN_REWARD
        for k in gitcoin_users
    }

    volume_reward = AIRDROP_PROGRAM - FIX_REWARD * len(fixed_rewards) - GITCOIN_REWARD * len(gitcoin_rewards)

    total_weight = sum(s['weight'] for s in inch_users.values())

    volume_rewards = {
        k: volume_reward * s['weight'] // total_weight
        for k, s in inch_users.items()
    }

    total_rewards = {}

    for d in [fixed_rewards, gitcoin_rewards, volume_rewards, first_liq_mining_rewards, second_liq_mining_rewards]:
        for u, r in d.items():
            if u not in total_rewards:
                total_rewards[u] = 0
            total_rewards[u] += r

    total_inch_rewards = sum(total_rewards.values())

    uniswap_users = process_uniswap_users(get_uniswap_users())
    for u in total_rewards:
        if u in uniswap_users:
            del uniswap_users[u]
    total_uniswap_weight = sum(uniswap_users.values())

    uniswap_volume_reward = UNISWAP_AIRDROP_PROGRAM - UNISWAP_FIX_REWARD * len(uniswap_users)

    for k, w in uniswap_users.items():
        if k in total_rewards:
            assert False
        total_rewards[k] = UNISWAP_FIX_REWARD + uniswap_volume_reward * w // total_uniswap_weight

    return total_rewards


def gen_third_distribution():
    prices = Prices(
        usdc_prices=get_usdc_prices(),
        usdt_prices=get_usdt_prices(),
        dai_prices=get_dai_prices(),
        eth_prices=get_eth_prices(),
    )

    lp_transfers = get_lp_transfers('data/bq-lp.csv')
    pools = list(lp_transfers.keys())

    first_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth.csv'),
        get_token_transfers(pools, 'data/bq-erc20.csv'),
        prices,
        FIRST_MINING_PROGRAM,
        FIRST_MINING_PROGRAM_START
    )

    lp_transfers = get_lp_transfers('data/bq-lp-2.csv')
    pools = list(lp_transfers.keys())

    second_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth-2.csv'),
        get_token_transfers(pools, 'data/bq-erc20-2.csv'),
        prices,
        SECOND_MINING_PROGRAM,
        SECOND_MINING_PROGRAM_START
    )

    inch_trades = get_1inch_trades('./data/dune-swaps-2.csv', './missing_traders_2.csv')
    limit_users = get_limit_users()
    relay_trades = get_relay_trades()
    inch_users = get_all_users(inch_trades, limit_users, relay_trades)

    gitcoin_users = get_gitcoin_users()

    fixed_rewards = {
        k: FIX_REWARD
        for k in inch_users
    }

    gitcoin_rewards = {
        k: GITCOIN_REWARD
        for k in gitcoin_users
    }

    volume_reward = AIRDROP_PROGRAM - FIX_REWARD * len(fixed_rewards) - GITCOIN_REWARD * len(gitcoin_rewards)

    total_weight = sum(s['weight'] for s in inch_users.values())

    volume_rewards = {
        k: volume_reward * s['weight'] // total_weight
        for k, s in inch_users.items()
    }

    total_rewards = {}

    for d in [fixed_rewards, gitcoin_rewards, volume_rewards, first_liq_mining_rewards, second_liq_mining_rewards]:
        for u, r in d.items():
            if u not in total_rewards:
                total_rewards[u] = 0
            total_rewards[u] += r

    total_inch_rewards = sum(total_rewards.values())

    uniswap_users = process_uniswap_users(get_uniswap_users())
    for u in total_rewards:
        if u in uniswap_users:
            del uniswap_users[u]
    total_uniswap_weight = sum(uniswap_users.values())

    uniswap_volume_reward = UNISWAP_AIRDROP_PROGRAM - UNISWAP_FIX_REWARD * len(uniswap_users)

    for k, w in uniswap_users.items():
        if k in total_rewards:
            assert False
        total_rewards[k] = UNISWAP_FIX_REWARD + uniswap_volume_reward * w // total_uniswap_weight
        uniswap_rewards[k] = UNISWAP_FIX_REWARD + uniswap_volume_reward * w // total_uniswap_weight

    return total_rewards
