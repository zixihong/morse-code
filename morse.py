import sys
import re

class Node:
    def __init__(self, value=None, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class Tree:
    def __init__(self):
        self.root = None
        self._used_chars = set()
        self._first_star = True
        self._token_pattern = re.compile(r'[()\-]|(?<=\s)[A-Za-z0-9*]+(?=\s|[)])|(?<=[(])[A-Za-z0-9*]+(?=\s|[)])')
        self._valid_data_re = re.compile(r'^[A-Z0-9]+$|^\*$')

    def parse(self, tree_string):
        if not tree_string or not tree_string.strip():
            return False

        tree_string = tree_string.strip()
        if not (tree_string.startswith('(') and tree_string.endswith(')')):
            return False

        try:
            tokens = [t.strip() for t in self._token_pattern.findall(tree_string) if t.strip()]
            self._token_iter = iter(tokens)
            self._used_chars.clear()
            self._first_star = True
            
            self.root = self._parse_node()
            
            if next(self._token_iter, None) is not None:
                return False
                
            if self.root is None or self.root.value != '*':
                return False
                
            return True
            
        except (StopIteration, ValueError):
            return False

    def _parse_node(self):
        try:
            token = next(self._token_iter)
        except StopIteration:
            return None

        if token == "-":
            return None
            
        elif token == "(":
            left = self._parse_node()
            
            try:
                value = next(self._token_iter)
            except StopIteration:
                raise ValueError()
                
            if not self._valid_data_re.match(value):
                raise ValueError()
                
            if value != "*":
                for char in value:
                    if char in self._used_chars:
                        raise ValueError()
                    self._used_chars.add(char)
            else:
                if self._first_star:
                    self._first_star = False
                    
            right = self._parse_node()
            
            try:
                closing_paren = next(self._token_iter)
            except StopIteration:
                raise ValueError()
                
            if closing_paren != ")":
                raise ValueError()
                
            return Node(value, left, right)
            
        else:
            value = token
            if not self._valid_data_re.match(value):
                raise ValueError()
                
            if value != "*":
                for char in value:
                    if char in self._used_chars:
                        raise ValueError()
                    self._used_chars.add(char)
            else:
                if self._first_star:
                    self._first_star = False
                    
            return Node(value)

    def build_maps(self):
        encoding = {}
        decoding = {}
        self._build_maps_helper(self.root, '', encoding, decoding)
        return encoding, decoding

    def _build_maps_helper(self, node, path, encoding, decoding):
        if not node:
            return
        if node.value and node.value != '*':
            decoding[path] = node.value
            for char in node.value:
                if char not in encoding or len(path) < len(encoding[char]):
                    encoding[char] = path
        self._build_maps_helper(node.left, path + '.', encoding, decoding)
        self._build_maps_helper(node.right, path + '-', encoding, decoding)

def encode_message(text, encoding):
    result = []
    for word in text.strip().upper().split():
        encoded_chars = []
        for char in word:
            if char in encoding:
                encoded_chars.append(encoding[char])
        if encoded_chars:
            result.append(" ".join(encoded_chars))
    return "  ".join(result)

def decode_message(morse_text, decoding):
    words = re.split(r'\s{2,}', morse_text.strip())
    result = []
    
    for word in words:
        chars = re.split(r'\s+', word.strip())
        decoded_word = ""
        index = 0
        
        while index < len(chars):
            found = False
            for end in range(len(chars), index, -1):
                code = ' '.join(chars[index:end])
                if code in decoding:
                    decoded_word += decoding[code]
                    index = end
                    found = True
                    break
            if not found:
                decoded_word += "?"
                index += 1
                
        if decoded_word:
            result.append(decoded_word)
            
    return " ".join(result)

def main():
    DEFAULT_TREE = "((((H S V) I (F U -)) E ((L R -) A (P W J))) * (((B D X) N (C K Y)) T ((Z G Q) M O)))"
    
    if len(sys.argv) not in [2, 3]:
        print("USAGE: morse.py [-e or -d] [tree-file]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode not in ["-e", "-d"]:
        print("USAGE: morse.py [-e or -d] [tree-file]")
        sys.exit(1)

    tree_content = DEFAULT_TREE
    if len(sys.argv) == 3:
        try:
            with open(sys.argv[2], 'r') as file:
                tree_content = file.read().strip()
                if not tree_content:
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
        except Exception:
            print("ERROR: Invalid tree file.")
            sys.exit(1)

    morse_tree = Tree()
    if not morse_tree.parse(tree_content):
        print("ERROR: Invalid tree file.")
        sys.exit(1)

    encoding, decoding = morse_tree.build_maps()

    for line in sys.stdin:
        if mode == "-e":
            print(encode_message(line, encoding))
        elif mode == "-d":
            print(decode_message(line, decoding))

main()