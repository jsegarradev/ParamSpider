#!/usr/bin/env python3
from core import requester
from core import extractor
from core import save_it
from urllib.parse import unquote
import argparse
import os
import sys
import time

start_time = time.time()

def process_urls_from_file(file_path, args):
    try:
        with open(file_path, 'r') as file:
            urls = file.read().splitlines()
            return process_urls(urls, args)
    except FileNotFoundError:
        print(f"\u001b[31m[!] File not found: {file_path}\u001b[0m")
        return []

def process_urls(urls, args):
    if not urls:
        print(f"\u001b[31m[!] No URLs found in the specified file.\u001b[0m")
        return []

    final_uris = []
    for url in urls:
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url  # Assume HTTP if no protocol is specified
        print(f"\n\u001b[32m[+] Processing URL: {url}\u001b[31m")
        response, retry = requester.connector(url)
        if response:
            response = unquote(response)
            black_list = []
            if args.exclude:
                if "," in args.exclude:
                    black_list = args.exclude.split(",")
                    black_list = ["." + item if not item.startswith('.') else item for item in black_list]
                else:
                    black_list.append("." + args.exclude)
            final_uris.extend(extractor.param_extract(response, args.level, black_list, args.placeholder))
    return final_uris

def main():
    if os.name == 'nt':
        os.system('cls')

    parser = argparse.ArgumentParser(description='ParamSpider a parameter discovery suite')
    parser.add_argument('-d', '--domain', help='Domain name of the target [ex: hackerone.com]')
    parser.add_argument('-s', '--subs', help='Set False for no subs [ex: --subs False]', default=True)
    parser.add_argument('-l', '--level', help='For nested parameters [ex: --level high]')
    parser.add_argument('-e', '--exclude', help='Extensions to exclude [ex: --exclude php,aspx]')
    parser.add_argument('-o', '--output', help='Output file name [by default it is \'domain.txt\']')
    parser.add_argument('-p', '--placeholder', help='The string to add as a placeholder after the parameter name.',
                        default="FUZZ")
    parser.add_argument('-q', '--quiet', help='Do not print the results to the screen', action='store_true')
    parser.add_argument('-r', '--retries', help='Specify number of retries for 4xx and 5xx errors', default=3)
    parser.add_argument('-f', '--file', help='File path containing URLs to process')

    args = parser.parse_args()

    if args.file:
        # Process URLs from the file
        final_uris = process_urls_from_file(args.file, args)
    elif args.domain:
        # Process a single URL specified by the user
        final_uris = process_urls([args.domain], args)
    else:
        print("\u001b[31m[!] Please provide either the -d option or the -f option.\u001b[0m")
        sys.exit(1)

    save_it.save_func(final_uris, args.output, args.domain)

    if not args.quiet:
        print("\u001b[32;1m")
        print('\n'.join(final_uris))
        print("\u001b[0m")

    print(f"\n\u001b[32m[+] Total number of retries:  {args.retries}\u001b[31m")
    print(f"\u001b[32m[+] Total unique URLs found : {len(final_uris)}\u001b[31m")
    if args.output:
        if "/" in args.output:
            print(f"\u001b[32m[+] Output is saved here :\u001b[31m \u001b[36m{args.output}\u001b[31m")
        else:
            print(f"\u001b[32m[+] Output is saved here :\u001b[31m \u001b[36moutput/{args.output}\u001b[31m")
    else:
        print(f"\u001b[32m[+] Output is saved here   :\u001b[31m \u001b[36moutput/{args.domain}.txt\u001b[31m")
    print("\n\u001b[31m[!] Total execution time      : %ss\u001b[0m" % str((time.time() - start_time))[:-12])

if __name__ == "__main__":
    main()

