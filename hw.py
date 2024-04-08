from typing import List, Any

import redis
from redis_lru import RedisLRU

from models import Author, Quote

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


@cache
def find_by_tag(tag: str) -> list[str | None]:
    print(f"Find by {tag}")
    quotes = Quote.objects(tags__iregex=tag)
    result = [q.quote for q in quotes]
    return result


@cache
def find_by_author(author: str) -> list[list[Any]]:
    print(f"Find by {author}")
    authors = Author.objects(fullname__iregex=author)
    result = {}
    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]
    return result


def search_quotes(command: str) -> None:
    parts = command.split(":", 1)
    if len(parts) != 2:
        print("Invalid command format. Please use 'name:', 'tag:', or 'tags:' followed by value.")
        return

    action, value = parts
    if action == "name":
        results = find_by_author(value.strip())
        print_results(results)
    elif action == "tag":
        results = find_by_tag(value.strip())
        print_results(results)
    elif action == "tags":
        tags = value.split(",")
        all_results = []
        for tag in tags:
            tag_results = find_by_tag(tag.strip())
            all_results.extend(tag_results)
        print_results(all_results)
    else:
        print("Invalid action. Please use 'name:', 'tag:', or 'tags:'.")


def print_results(results: List[str] or dict[str, List[Any]]) -> None:
    if isinstance(results, dict):
        for author, quotes in results.items():
            print(f"Author: {author}")
            for quote in quotes:
                print(f"- {quote}")
    elif isinstance(results, list):
        for quote in results:
            print(f"- {quote}")


if __name__ == "__main__":
    while True:
        command = input("Enter command ('name:', 'tag:', 'tags:', or 'exit' to quit): ").strip()
        if command.lower() == "exit":
            break
        search_quotes(command)

