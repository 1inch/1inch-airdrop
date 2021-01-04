from distribution import gen_second_distribution, print_distribution


def main():
    print_distribution(gen_second_distribution(), 'second_distribution.json')


if __name__ == '__main__':
    main()