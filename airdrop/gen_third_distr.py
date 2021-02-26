from distribution import gen_second_distribution, gen_third_distribution, print_distribution


def main():
    second_distr, _ = gen_second_distribution()
    third_distr, _ = gen_third_distribution()
    updated_distr = {}

    for u, t in third_distr.items():
        extra_tokens = t - (second_distr.get(u) or 0)
        if extra_tokens > 0:
            updated_distr[u] = extra_tokens

    distr = {}
    for k, v in updated_distr.items():
        if k not in second_distr:
            distr[k] = 600 * 10 ** 18
        elif v > 600e18:
            if second_distr[k] < 600e18:
                distr[k] = 600 * 10 ** 18

    print_distribution(distr, 'third_distribution.json')


if __name__ == '__main__':
    main()