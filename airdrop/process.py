from operator import attrgetter

from airdrop.config import SEPT_15, ZERO_ADDR, USDC_ADDR, USDT_ADDR, DAI_ADDR
from airdrop.structs import LPTransfer, TokenTransfer, Operation, Price


def _get_1inch_users(trades):
    user_trades = dict()

    for t in trades:
        if t.tx_from not in user_trades:
            user_trades[t.tx_from] = []
        user_trades[t.tx_from].append(t)

    assert sum(len(v) for v in user_trades.values()) == len(trades)

    user_stats = dict()

    for u, ts in user_trades.items():
        user_stats[u] = {
            'volume': sum(max(t.from_usd, t.to_usd) for t in ts),
            'count': len(ts),
            'first_trade': min(t.block_time.timestamp() for t in ts),
            'weight': int((sum(max(t.from_usd, t.to_usd) for t in ts) ** (2 / 3)) * 1000),
        }

    return user_stats


def get_all_users(trades, limit_order_users, relay_trades):
    all_users = _get_1inch_users(trades)
    for u in limit_order_users:
        user = all_users.get(u.maker)
        if user is None:
            user = {
                'volume': 0,
                'count': 0,
                'first_trade': 0xfffffffffffffff
            }
        user['volume'] += u.volume if u.volume is not None else 0
        user['count'] += u.trades
        user['first_trade'] = min(user['first_trade'], u.first_trade)
        user['weight'] = int((user['volume'] ** (2 / 3)) * 1000)
        all_users[u.maker] = user
    
    relay_users = _get_1inch_users(relay_trades)
    for u, s in relay_users.items():
        user = all_users.get(u)
        if user is None:
            user = {
                'volume': 0,
                'count': 0,
                'first_trade': 0xfffffffffffffff
            }
        user['volume'] += s['volume']
        user['count'] += s['count']
        user['first_trade'] = min(user['first_trade'], s['first_trade'])
        user['weight'] = int((user['volume'] ** (2 / 3)) * 1000)
        all_users[u] = user
    
    filtered_users = {u: s for u, s in all_users.items() if
                      s['first_trade'] <= SEPT_15 or s['volume'] >= 20 or s['count'] > 3}
    return filtered_users
    

def get_1inch_users(trades):
    filtered_users = {u: s for u, s in _get_1inch_users(trades).items() if
                      s['first_trade'] <= SEPT_15 or s['volume'] >= 20 or s['count'] > 3}

    return filtered_users


def calculate_users_usdsec(all_events, tracked_token, start_timestamp):
    user_share = dict()
    user_usd_sec = dict()
    pool_total_supply = 0
    pool_total_tokens = 0
    prev_price = 0
    last_processed_sec = start_timestamp

    for op in all_events:
        if last_processed_sec < op.timestamp and prev_price > 0:
            # update all users contributions
            total_usd_sec = (op.timestamp - last_processed_sec) * pool_total_tokens * 2 / prev_price
            if total_usd_sec < 0:
                print(op.timestamp, last_processed_sec, pool_total_tokens, prev_price)
                assert False
            for user, share in user_share.items():
                if user not in user_usd_sec:
                    user_usd_sec[user] = 0
                user_usd_sec[user] += total_usd_sec * share / pool_total_supply

        # process next event
        if type(op).__name__ == LPTransfer.__name__:
            if op.addr_from == ZERO_ADDR:
                # mint
                if op.addr_to != op.pool:
                    if op.addr_to not in user_share:
                        user_share[op.addr_to] = 0
                    user_share[op.addr_to] += op.amount
                pool_total_supply += op.amount
            elif op.addr_to == ZERO_ADDR:
                # burn
                if op.addr_from not in user_share:
                    user_share[op.addr_from] = 0
                    assert op.amount == 0
                user_share[op.addr_from] -= op.amount
                pool_total_supply -= op.amount
            else:
                # transfer
                if op.addr_from not in user_share:
                    user_share[op.addr_from] = 0
                    assert op.amount == 0
                if op.addr_to not in user_share:
                    user_share[op.addr_to] = 0
                user_share[op.addr_to] += op.amount
                user_share[op.addr_from] -= op.amount
        elif type(op).__name__ == TokenTransfer.__name__:
            if op.token == tracked_token:
                if op.operation == Operation.ADDITION:
                    pool_total_tokens += op.amount
                elif op.operation == Operation.REMOVAL:
                    pool_total_tokens -= op.amount
                else:
                    assert False
        elif type(op).__name__ == Price.__name__:
            prev_price = op.price
        else:
            assert False
        
        if last_processed_sec < op.timestamp:
            last_processed_sec = op.timestamp

    return user_usd_sec


def process_mining_program(lp_transfers, eth_transfers, token_transfers, prices, program_amount_total, program_start):
    pools = list(lp_transfers.keys())

    all_transfers = {
        pool: sorted(lp_transfers[pool] + token_transfers[pool] + (eth_transfers.get(pool) or []),
                     key=attrgetter('timestamp'))
        for pool in pools
    }

    all_usd_sec = dict()

    for pool, transfers in all_transfers.items():
        tracked_token = None
        selected_prices = None
        for transfer in transfers:
            if type(transfer).__name__ == TokenTransfer.__name__:
                if transfer.token == USDC_ADDR:
                    tracked_token = USDC_ADDR
                    selected_prices = prices.usdc_prices
                elif transfer.token == USDT_ADDR:
                    tracked_token = USDT_ADDR
                    selected_prices = prices.usdt_prices
                elif transfer.token == DAI_ADDR:
                    tracked_token = DAI_ADDR
                    selected_prices = prices.dai_prices
                elif transfer.token == ZERO_ADDR:
                    tracked_token = ZERO_ADDR
                    selected_prices = prices.eth_prices
                else:
                    continue
                break
        assert tracked_token is not None
        assert selected_prices is not None
        events = sorted(transfers + selected_prices, key=attrgetter('timestamp'))
        user_usd_sec = calculate_users_usdsec(events, tracked_token, program_start)
        all_usd_sec[pool] = user_usd_sec
        print('processed', pool)

    total_usd_sec = []
    user_usd_sec = dict()

    for pool_usd_sec in all_usd_sec.values():
        for user, amount in pool_usd_sec.items():
            if user not in user_usd_sec:
                user_usd_sec[user] = []
            user_usd_sec[user].append(amount)
            total_usd_sec.append(amount)

    total_usd_sec = int(sum(sorted(total_usd_sec)))

    tokens = {
        user: program_amount_total * int(sum(sorted(usd_sec))) // total_usd_sec
        for user, usd_sec in user_usd_sec.items()
    }

    return tokens
