SELECT * FROM (
SELECT
    '0x' || encode(tx_from, 'hex') as wallet,
    SUM(GREATEST(from_usd, to_usd)) AS volume,
    count(*) as swaps,
    MIN(block_time) as "start",
    MAX(block_time) as "stop",
    pow(1 + SUM(GREATEST(from_usd, to_usd)), 0.5) as reward
FROM (
    SELECT tx_from, to_token, from_token, to_amount, from_amount, tx_hash, block_time, from_usd, to_usd FROM oneinch.view_swaps UNION ALL
    SELECT tx_from, to_token, from_token, to_amount, from_amount, tx_hash, block_time, from_usd, to_usd FROM onesplit.view_swaps
    WHERE tx_hash NOT IN (SELECT tx_hash FROM oneinch.view_swaps) UNION ALL
    SELECT tx_from, to_token, from_token, to_amount, from_amount, tx_hash, block_time, from_usd, to_usd FROM oneproto.view_swaps
    WHERE tx_hash NOT IN (SELECT tx_hash FROM oneinch.view_swaps)
) oi
group by 1
order by 3 desc, 2 desc nulls last
) tt
where (volume is null and swaps >= 3)
or (volume > 100 and (swaps > 3 or volume > 100))
