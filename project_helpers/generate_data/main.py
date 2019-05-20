import argparse

from generate_data import generate_data

parser = argparse.ArgumentParser(description='Generate random data')
parser.add_argument('path', type=str,
                    help='Path to save the generated data')
parser.add_argument('--loans', default=50, type=int,
                    help='Define how much Loans will created')
parser.add_argument('--clients', default=10, type=int,
                    help='Define how much Clients will created')

args = parser.parse_args()
generate_data(args.loans, args.clients, args.path)
