from pathlib import Path
import re


def __fuzzyfinder(input, items, sort_results=True):
    func = lambda someting: someting
    results = []
    input = str(input) if not isinstance(input, str) else input
    pattern = ".*?".join(map(re.escape, input))
    pattern = "(?=({0}))".format(pattern)
    regex = re.compile(pattern)
    for item in items:
        r = list(regex.finditer(func(item)))
        if r:
            best = min(r, key=lambda x: len(x.group(1)))  # find shortest match
            results.append((len(best.group(1)), best.start(), func(item), item))
    if sort_results:
        return (z[-1] for z in sorted(results))
    else:
        return (z[-1] for z in sorted(results, key=lambda x: x[:2]))


class ContentNotFoundError(Exception): ...


class PackageNotFoundError(Exception): ...


class ContentPackage:
    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.strpath = path
        self.path = Path(path)

    def AllContent(self):
        results = []
        for dirpath, _, filenames in self.path.walk():
            if dirpath == self.path:
                for file in filenames:
                    results.append(file)
        return results

    def getContent(self, name: str):
        for dirpath, _, filenames in self.path.walk():
            if dirpath == self.path:
                for file in filenames:
                    if Path(file).name == name:
                        return dirpath / Path(file)
        raise ContentNotFoundError(f"content batch with the name {name!r} not found!")

    def __repr__(self):
        return f"{self.name}/"


class ContentManager:
    def __init__(self) -> None:
        self.packages: list[ContentPackage] = []

    def register(self, package: ContentPackage):
        self.packages.append(package)

    def getPackage(self, name: str) -> ContentPackage:
        for package in self.packages:
            if package.name == name:
                return package
        raise PackageNotFoundError(f"package with the name {name!r} not found!")


def search(string: str, package: ContentPackage) -> list[str]:
    return list(__fuzzyfinder(string, package.AllContent()))
