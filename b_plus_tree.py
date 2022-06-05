"""Simple implementation of a B+ tree, a self-balancing tree data structure that (1) maintains sort
data order and (2) allows insertions and access in logarithmic time.
"""
from __future__ import annotations

import roman
import argparse
import random

class Node(object):
    """Base node object.
    Each node stores keys and values. Keys are not unique to each value, and as such values are
    stored as a list under each key.
    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order):
        """Child nodes can be converted into parent nodes by setting self.is_leaf = False. Parent nodes
        simply act as a medium to traverse the tree."""
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
            # If new key matches existing key, add to list of values.
            if key == item:
                self.values[i].append(value)
                break

            # If new key is smaller than existing key, insert new key to the left of existing key.
            elif key < item:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If new key is larger than all existing keys, insert new key to the right of all
            # existing keys.
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
        """Returns True if the node is full."""
        return len(self.keys) == self.order

    # def show(self, counter=0):
    #     """Prints the keys at each level."""
    #     for key, value in enumerate(self.keys):
    #         print(counter, f"{key} -> {value}")
    def show(self, counter=0):
        """Prints the keys at each level."""
        print(f"{counter}, {str(self.keys)}")
        print(f"{' ' * len(str(counter))}, {str(self.values)}")

        # Recursively print the key of child nodes (if these exist).
        if not self.is_leaf:
            for item in self.values:
                item.show(counter + 1)

class BPlusTree:
    """B+ tree object, consisting of nodes.
    Nodes will automatically be split into two once it is full. When a split occurs, a key will
    'float' upwards and be inserted into the parent node to act as a pivot.
    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order=4):
        self.root = Node(order)

    def _find(self, node, key):
        """ For a given node and key, returns the index where the key should be inserted and the
        list of values at that index."""
        for i, item in enumerate(node.keys):
            if key < item:
                return node.values[i], i

        return node.values[i + 1], i + 1

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
        the leaf node into two."""
        parent = None
        child = self.root

        # Traverse tree until leaf node is reached.
        while not child.is_leaf:
            parent = child
            child, index = self._find(child, key)

        child.add(key, value)

        # If the leaf node is full, split the leaf node into two.
        if child.is_full():
            child.split()

            # Once a leaf node is split, it consists of a internal node and two leaf nodes. These
            # need to be re-inserted back into the tree.
            if parent and not parent.is_full():
                self._merge(parent, child, index)

    def retrieve(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        child = self.root

        while not child.is_leaf:
            child, index = self._find(child, key)

        for i, item in enumerate(child.keys):
            if key == item:
                return child.values[i]

        return None

    def show(self):
        """Prints the keys at each level."""
        self.root.show()



def demo_bplustree(order=12):
    bplustree = BPlusTree(order=order)
    print(f'\nB+ tree with {order} item(s)...')
    bplustree.insert(str(0), 'nulla')
    for i in range(1, order + 1):
        bplustree.insert(str(i), roman.toRoman(i))
        
    
    print("Full Tree:\n")
    bplustree.show()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()

    parser.add_argument('--order', type=int, help='B+ Tree order as int. 12 is used as default')
    print(parser.format_help())

    parser_args=parser.parse_args()
    order = parser_args.order
    demo_bplustree(order=order)