from distribution import gen_initial_distribution, print_distribution


def main():
    print_distribution(gen_initial_distribution(), 'initial_distribution.json')


if __name__ == '__main__':
    main()