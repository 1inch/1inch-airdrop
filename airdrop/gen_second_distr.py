from distribution import gen_initial_distribution, gen_second_distribution, print_distribution


def main():
    initial_distr = gen_initial_distribution()
    second_distr, _ = gen_second_distribution()
    updated_distr = {}

    for u, t in second_distr.items():
        extra_tokens = t - (initial_distr.get(u) or 0)
        if extra_tokens >= 1e18:
            updated_distr[u] = extra_tokens

    print_distribution(updated_distr, 'second_distribution.json')


if __name__ == '__main__':
    main()