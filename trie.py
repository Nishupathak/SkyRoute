class TrieNode:
    def __init__(self):
        self.children = {}
        self.codes = set()


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, code):
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
        node.codes.add(code)

    def suggest(self, prefix, limit=5):
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return []
            node = node.children[ch]
        found = set()
        stack = [node]
        while stack:
            current = stack.pop()
            found.update(current.codes)
            stack.extend(current.children.values())
        return sorted(found)[:limit]