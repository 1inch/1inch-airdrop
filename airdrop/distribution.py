import json

from airdrop.config import FIRST_MINING_PROGRAM, SECOND_MINING_PROGRAM, FIX_REWARD, GITCOIN_REWARD, AIRDROP_PROGRAM
from airdrop.parse import get_usdc_prices, get_usdt_prices, get_dai_prices, get_eth_prices, get_lp_transfers, \
    get_eth_transfers, get_token_transfers, get_1inch_trades, get_gitcoin_users
from airdrop.process import process_mining_program, get_1inch_users
from airdrop.structs import Prices


def print_distribution(all_rewards):
    with open('distribution.json', 'w') as out_f:
        d = {
            k: hex(v)[2:]
            for k, v in all_rewards.items()
            if v > 0
        }
        json.dump(d, out_f)


def gen_distribution():
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
        FIRST_MINING_PROGRAM
    )

    lp_transfers = get_lp_transfers('data/bq-lp-2.csv')
    pools = list(lp_transfers.keys())

    second_liq_mining_rewards = process_mining_program(
        lp_transfers,
        get_eth_transfers(pools, 'data/bq-eth-2.csv'),
        get_token_transfers(pools, 'data/bq-erc20-2.csv'),
        prices,
        SECOND_MINING_PROGRAM
    )

    inch_trades = get_1inch_trades()
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


if __name__ == '__main__':
    print_distribution(gen_distribution())
