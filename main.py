import argparse
from match import match
from scanner import scan

def main():
    parser = argparse.ArgumentParser(description="human based file finder")
    parser.add_argument("query", type=str, help="file to find", nargs='+')
    parser.add_argument("--dir", type=str, default=".", help="directory to look in")
    parser.add_argument("--type", type=str, help="filter by extension")
    parser.add_argument("--limit", type=int, default=3, help="max results to show")
    parser.add_argument("--hidden", action="store_true", help="go through hidden files")

    args = parser.parse_args()

    scanned = scan(args.dir, hidden=args.hidden)

    if args.type:
        extension = args.type.lower().lstrip(".")
        scanned = [f for f in scanned if f.lower().endswith(f".{extension}")]
    
    results = match(scanned, args.query)

    if not results:
        print("no matches found, try another query")
        return
    
    shown = results[:args.limit]
    print(f"{len(results)} results found (showing top {len(shown)})")
    for i, path in enumerate(shown, 1):
        print(f"{i:>2}. {path}")

if __name__ == "__main__":
    main()
