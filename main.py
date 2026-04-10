import argparse
from match import match
from scanner import scan

def main():
    parser = argparse.ArgumentParser(description="human based file finder")
    parser.add_argument("query", type=str, help="file to find", nargs='+')
    parser.add_argument("--dir", type=str, help="directory to look in")

    args = parser.parse_args()

    if args.query:
        scanned = scan("/Users/divpreet")
        results = match(scanned, args.query)
        print(results)
    elif args.dir:
        print(args.dir)

main()
