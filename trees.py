"""Binomial real options pricing
Implemented according to paper:
https://www.researchgate.net/publication/255998648_Opcje_rzeczywiste_rzeczowe_realne_jako_metoda_oceny_efektywnosci_inwestycji_w_warunkach_niepewnosci_ryzyka

Usage:
  trees.py base_instrument <n> <income> <volatility>
  trees.py internal_value <n> <income> <volatility> <rf> <inv> <decline>
  trees.py delay_option_value <n> <income> <volatility> <rf> <inv> <decline>
  trees.py (-h | --help)
  trees.py (-v | --version)

Options:
  -h --help     Show this screen.
  -v --version     Show version.

Examples from paper:
  trees.py base_instrument 2 90 0.3
  trees.py internal_value 2 90 0.3 0.06 100 0.05
  trees.py delay_option_value 2 90 0.3 0.06 100 0.05

Jakub Stepniak, 2016
https://github.com/nbbn
"""
from docopt import docopt
import numpy as np
import copy


def base_instr(periods, base_price, volatility):
    u = np.exp(volatility)
    d = np.exp(-volatility)
    base_price = [[base_price]]
    for i in range(periods):
        tmp = []
        for s in base_price[-1]:
            if len(tmp) == 0:
                tmp += [s * u]
            tmp += [s * d]
        base_price.append(tmp)
    return base_price


def internal_value_of_options(periods, base_price, investment, volatility):
    u = np.exp(volatility)
    d = np.exp(-volatility)
    base_price = [[base_price]]
    for i in range(periods):
        tmp = []
        for s in base_price[-1]:
            if len(tmp) == 0:
                tmp += [s * u]
            tmp += [s * d]
        base_price.append(tmp)
    for i in range(periods + 1):
        pos = -1
        for s in base_price[i]:
            pos += 1
            if s - investment < 0:
                base_price[i][pos] = 0
            else:
                base_price[i][pos] = s - investment
    return base_price


def delay_option_value(periods, base_price, rf, investment, decline, volatility):
    u = np.exp(volatility)
    d = np.exp(-volatility)
    q = (np.exp(rf - decline) - d) / (u - d)
    tmp = internal_value_of_options(periods, base_price, investment, volatility)
    war_opc = copy.deepcopy(tmp)
    for i in range(periods - 1, -1, -1):
        pos = -1
        for s in war_opc[i]:
            pos += 1
            position_intern_val = (q * war_opc[i + 1][pos] + (1 - q) * war_opc[i + 1][pos + 1]) * np.exp(-rf)
            if position_intern_val > tmp[i][pos]:
                war_opc[i][pos] = position_intern_val
            else:
                war_opc[i][pos] = tmp[i][pos]
    return war_opc


def print_tree(tree):
    for position in range(len(tree[-1])):
        for x in tree:
            try:
                print('{:06.2f}'.format(x[position]), end='\t')
            except IndexError:
                print(' ' * 6, end='\t')
        print('')


def run():
    arguments = docopt(__doc__, version='Trees 0.1')
    n = int(arguments['<n>'])
    start_price = float(arguments['<income>'])
    volatility = float(arguments['<volatility>'])
    if arguments['base_instrument']:
        r_tree = base_instr(n, start_price, volatility)
        print_tree(r_tree)
    elif arguments['internal_value']:
        inv = float(arguments['<inv>'])
        r_tree = internal_value_of_options(n, start_price, inv, volatility)
        print_tree(r_tree)
    elif arguments['delay_option_value']:
        rf = float(arguments['<rf>'])
        inv = float(arguments['<inv>'])
        decline = float(arguments['<decline>'])
        r_tree = delay_option_value(n, start_price, rf, inv, decline, volatility)
        print_tree(r_tree)


if __name__ == '__main__':
    run()
