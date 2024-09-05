import argparse

parser = argparse.ArgumentParser(description='cis 2.17.1 upgrade tools')
parser.add_argument('--files', type=str, help='cis deployments need to update')
parser.add_argument('--image', type=str, help='new cis image')
parser.add_argument('--interval', type=str, help='cis sync interval')
parser.add_argument('--label', type=str, help='cis watch namespace label')
parser.add_argument('--cm', action='store_true', default=False, help='add label to configmap')
cli = parser.parse_args()

print(cli.files)
print(cli.image)
print(cli.interval)
print(cli.label)

if cli.files:
   print("===")

print(cli.cm)
