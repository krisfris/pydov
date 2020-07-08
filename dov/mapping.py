import os
import re
import sys
import json
import random
import datetime
import itertools
from collections import Counter, deque

import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt

import config


exclude_keys = ['backspace', 'right', 'left', 'up', 'down', 'space', 'return',
                'super_l', 'control_l', 'shift_l', 'shift_r', 'alt_l', 'control_r', 'super_r']


def read_keylog():
    for line in open(os.path.join(config.datadir, 'keys.log')):
        d = json.loads(line)
        if d['process'] not in config.excluded_process_names and \
           d['window'] not in config.excluded_window_names and \
           d['key'].lower() not in exclude_keys and \
           not re.match(r'\[.+\]$', d['key']):
            yield d


def calc_freqs_single():
    keys = [x['key'].lower() for x in read_keylog() if x['action'] == 'key down']
    c = Counter(keys)
    json.dump(c.most_common(), open(os.path.join(config.datadir, 'freqs_single.json'), 'w'))


def calc_freqs_pairs():
    keys = [x['key'].lower() for x in read_keylog() if x['action'] == 'key down']
    pairs = [(a, b) for a, b in zip(keys, keys[1:]) if a != b]
    c = Counter(pairs)
    json.dump(c.most_common(), open(os.path.join(config.datadir, 'freqs_pairs.json'), 'w'))


def input_difficulty(inp):
    return len(inp[0]) + len(inp[1])


def possible_inputs_per_stick():
    return [(0,), (1,), (2,), (3,), (0, 1), (0, 3), (1, 0), (1, 2), (2, 1), (2, 3),
            (3, 2), (3, 0), (0, 1, 2), (0, 3, 2), (1, 0, 3), (1, 2, 3), (2, 1, 0), (2, 3, 0),
            (3, 0, 1), (3, 2, 1)]


def group_keys(keys, pair_freqs):
    pair_freqs = [x for x in pair_freqs if x[0][0] in keys and x[0][1] in keys]

    def remove_lowest_weight_edge(graph):
        lowest_weight_edge = sorted(graph.edges(data=True), key=lambda x: x[2]['weight'])[0]
        graph.remove_edge(lowest_weight_edge[0], lowest_weight_edge[1])

    def merge_bipartite_sets(sets):
        sets = iter(sets)
        result = next(sets)
        for s in sets:
            for src, dst in zip(sorted(result, key=len),
                sorted(s, key=len, reverse=True)):
                    src |= dst
        return result

    def show_graph(graph, bipartite=None):
        weights = [w for (_, _, w) in graph.edges.data('weight')]
        if bipartite:
            pos = nx.bipartite_layout(graph, bipartite)
        else:
            pos = nx.circular_layout(graph)
        nx.draw_networkx(graph, pos, with_labels=True,
                         width=[x * len(weights) / sum(weights)
                                for x in weights])
        nx.draw_networkx_edge_labels(graph,
                                     pos,
                                     edge_labels=nx.get_edge_attributes(graph, 'weight'))
        plt.show()

    def bipartite_sets(graph):
        while True:
            try:
                bottom_nodes, top_nodes = bipartite.sets(graph)
            except nx.NetworkXError as e:
                if str(e) != 'Graph is not bipartite.':
                    raise
                remove_lowest_weight_edge(graph)
            except nx.AmbiguousSolution as e:
                if not str(e).startswith('Disconnected graph'):
                    raise
                return merge_bipartite_sets([bipartite_sets(x)
                    for x in (graph.subgraph(c).copy() for c in nx.connected_components(graph))])
            except:
                show_graph(graph)
                raise
            else:
                return bottom_nodes, top_nodes

    graph = nx.Graph()
    graph.add_nodes_from(keys)

    # Add edges; since undirected sum weights for opposite directions to avoid overwrite
    for (a, b), f in pair_freqs:
        if graph.has_edge(b, a):
            graph[b][a]['weight'] += f
        else:
            graph.add_edge(a, b, weight=f)

    return bipartite_sets(graph)


def gen_single_stick_mappings(single_freqs, pair_freqs, keymap):
    inputs = list(itertools.chain.from_iterable(((tuple(), x), (x, tuple()))
                                                for x in possible_inputs_per_stick()))
    for difficulty, group in itertools.groupby(sorted(inputs, key=input_difficulty),
                                               key=input_difficulty):
        left, right = [], []
        for inp in group:
            (left if len(inp[0]) == 0 else right).append(inp)

        assert len(left) == len(right)  # The rest assumes equal number of inputs on each side

        keys = [single_freqs.popleft()[0] for _ in range(len(left) + len(right))]
        bottom, top = group_keys(keys, pair_freqs)

        # This seems to work but not sure if it's guaranteed
        assert len(bottom) == len(left) and len(top) == len(right)

        for keys, inputs in ((bottom, left), (top, right)):
            for key, inp in zip(keys, inputs):
                keymap[inp] = key


def gen_combined_mappings(single_freqs, keymap):
    inputs = itertools.product(possible_inputs_per_stick(), repeat=2)

    def gen_inputs():
        for difficulty, group in itertools.groupby(sorted(inputs, key=input_difficulty),
                                                   key=input_difficulty):
            group = list(group)
            random.shuffle(group)
            yield from group

    for inp, (key, _) in zip(gen_inputs(), single_freqs):
        keymap[inp] = key


def gen_mappings():
    single_freqs = deque(json.load(open(os.path.join(config.datadir, 'freqs_single.json'))))
    pair_freqs = json.load(open(os.path.join(config.datadir, 'freqs_pairs.json')))
    keymap = dict()
    gen_single_stick_mappings(single_freqs, pair_freqs, keymap)
    gen_combined_mappings(single_freqs, keymap)
    json.dump(list(keymap.items()), open(os.path.join(config.datadir, 'keymap.json'), 'w'))


if __name__ == '__main__':
    calc_freqs_single()
    calc_freqs_pairs()
    gen_mappings()
