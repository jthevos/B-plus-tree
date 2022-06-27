from __future__ import annotations

import roman
import argparse


class Node(object):
    """Each node stores keys and values. Keys are not unique to each value
    and are stored as a list under each key.
    """

    def __init__(self, order=4):
        """Child nodes can be converted into parent nodes by setting self.is_leaf = False.
        Parent nodes act as means by which we traverse the tree."""
        self.order = order
        self.keys = []
        self.values = []
        self.is_leaf = True

    def add(self, key, value) -> None:
        """Adds a key-value pair to the node."""

        # If the node is empty, simply insert the key-value pair.
        if not self.keys:
            self.keys.append(key)
            self.values.append([value])
            return

        for i, item in enumerate(self.keys):
            # If new key matches existing key, append the supplied value to its list of values.
            if key == item:
                self.values[i].append(value)
                break

            # If new key is smaller than existing key, insert new key in the left-most position.
            elif key < item:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If new key is larger than all existing keys, insert new key in the right-most position.
            elif i + 1 == len(self.keys):
                self.keys.append(key)
                self.values.append([value])

    def split(self):
        """Splits the node into two and stores them as child nodes."""
        left = Node(self.order)
        right = Node(self.order)
        mid = self.order // 2  # Integer division with a built in round down

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        right.keys = self.keys[mid:]
        right.values = self.values[mid:]

        # When the node is split, set the parent key to the left-most key of the right child node.
        self.keys = [right.keys[0]]
        self.values = [left, right]
        self.is_leaf = False

    def is_full(self):
        """Returns True if the node is full"""
        return len(self.keys) == self.order

    def render(self, counter=0):
        """Prints the keys at each level."""
        print(f"{counter}, {str(self.keys)}")
        print(
            f"{' ' * len(str(counter))}, {str(self.values)}"
        )  # Preserve indentation for output readability

        # Recursively print the key of child nodes if these exist.
        if not self.is_leaf:
            for value in self.values:
                value.render(counter + 1)


class BPlusTree:
    """B+ tree object containing nodes. Nodes will automatically be split once full.
    If a split is required, a new key will be interted into the main tree and act as a pivot for
    the tree to self-balance.

    `_search` and `_merge` are only used interally by `fetch` and `insert` respectively.
    """

    def __init__(self, order=4):
        """Only a single node is required to begin the tree."""
        self.root = Node(order)

    def _search(self, node, key):
        """For a given node and key, return the index where the key should be inserted and the
        list of values at that index."""
        for i, item in enumerate(node.keys):
            if key < item:
                return i, node.values[i]

        return i + 1, node.values[i + 1]

    def _merge(self, parent, child, index):
        """For a parent and child node, extract a pivot from the child to be inserted into the keys
        of the parent. Insert the values from the child into the values of the parent.
        """
        parent.values.pop(index)
        pivot = child.keys[0]

        for i, item in enumerate(parent.keys):
            if pivot < item:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break

            elif i + 1 == len(parent.keys):
                parent.keys += [pivot]
                parent.values += child.values
                break

    def insert(self, key, value):
        """Inserts a key-value pair after traversing to a leaf node. If the leaf node is full, split
        the node."""
        parent = None
        child = self.root

        # Parent nodes exist only for traversal. We must find a leaf.
        while not child.is_leaf:
            parent = child
            index, child = self._search(child, key)

        child.add(key, value)

        # Split the node if full.
        if child.is_full():
            child.split()

            # Once a leaf node is split, it consists of a internal node and two leaf nodes. These
            # need to be re-inserted back into the tree.
            if parent and not parent.is_full():
                self._merge(parent, child, index)

    def fetch(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        child = self.root

        while not child.is_leaf:
            _, child = self._search(child, key)

        for i, item in enumerate(child.keys):
            if key == item:
                return child.values[i]

        return None

    def render(self):
        """Prints the keys at each level."""
        self.root.render()


def demo_bplustree(order):
    """In order to accommodate for arbitrary tree order, roman numerals are used as values.
    Because the concept of zero as a number originates after roman numerals were retired,
    'N' is the zero character.
    """
    bplustree = BPlusTree(order)

    for i in range(0, order):
        bplustree.insert(str(i), roman.toRoman(i))

    print(f"\nB+ tree with order {order}:\n")
    bplustree.render()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--order", type=int, help="B+ Tree order as int. 12 is used as default"
    )
    print(parser.format_help())

    parser_args = parser.parse_args()
    order = parser_args.order or 4
    demo_bplustree(order=order)
