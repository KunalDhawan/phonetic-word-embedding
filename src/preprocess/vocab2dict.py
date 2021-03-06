"""
Vocab2Dict
==========

Converts vocab file (from LM) to dictionary file.
"""

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter

class Vocab2Dict:

    def __init__(self, map_file):
        self.vocab = self.load_vocab(map_file)
        self.words = set()
        self.persian = {
            'क': 'क़',
            'ख': 'ख़',
            'ग': 'ग़',
            'ज': 'ज़',
            'ड': 'ड़',
            'ढ': 'ढ़',
            'फ': 'फ़',
            'य': 'य़',
            'न': 'ऩ',
            'र': 'ऱ',
            'झ': 'झ़'
        }

    def load_vocab(self, map_file):
        vocab = {}
        with open(map_file, 'r', encoding='utf-8') as f:
            header = None
            for line in f:
                row = line.strip().split(',')
                if header is None:
                    header = row
                else:
                    d = dict(zip(header, row))
                    vocab[d['symbol']] = d
        return vocab

    def add(self, word):
        word = word.replace('▁', ' ').strip()
        new_word = ''
        for i, c in enumerate(word):
            if c in self.vocab:
                d = self.vocab[c]
                if i == 0 and d['type'] == 'matra':
                    print(word, 'invalid position (can not start with matra) (', c, ') ->', d)
                    return False
                elif d['info'] in ['sanskrit']:
                    print(word, 'excluding (', c, ') ->', d)
                    return False
                # elif d['info'] in ['start'] and i > 0:
                #     print('invalid position (should only be in start) (', c, ') ->', d)
                #     return False
                elif d['info'] in ['after', 'nukta'] and i == 0:
                    print(word, 'invalid position (can not be in start) (', c, ') ->', d)
                    return False
                elif d['info'] == 'nukta':
                    prev = word[i - 1]
                    if prev in self.persian:
                        new_word = new_word[:-1] + self.persian[prev]
                    else:
                        print(word, 'invalid nukta addition with (', prev, ') ->', self.vocab[prev])
                        return False
                else:
                    new_word += c
            else:
                print(word, 'not found in vocab (', c, ')')
                return False
        if new_word:
            self.words.add(new_word)
        return True


def _main(args):
    converter = Vocab2Dict(args.phone)
    with open(args.vocab, "r", encoding='utf-8') as in_file:
        for line in in_file:
            words = line.strip().split()
            if not converter.add(words[0]):
                print('word', words[0], 'ignored')

    with open(args.output, 'w', encoding='utf-8') as out_file:
        description = f'; Autogenerated file using {os.path.basename(__file__)}\n' \
            + f'; Phonetic file: {args.phone}\n' \
            + f'; Vocab file: {args.vocab}\n'
        out_file.write(description)
        for word in sorted(converter.words):
            out_file.write(word)
            out_file.write('\n')


def _get_args():
    parser = ArgumentParser(
        os.path.basename(__file__), description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("phone", type=str, help='phone information file')
    parser.add_argument("vocab", type=str, help='LM vocab file')
    parser.add_argument("output", type=str, help='output dictionary file')
    return parser.parse_args()

if __name__ == '__main__':
    _main(_get_args())
