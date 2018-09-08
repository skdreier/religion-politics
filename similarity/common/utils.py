import mmap
import os

from tqdm import tqdm


def pbar_line_generator(path, encoding='utf-8'):
    with open(path, 'r+', encoding=encoding) as f:
        with mmap.mmap(f.fileno(), 0) as buf:
            n_lines = 0
            while buf.readline():
                n_lines += 1

        for line in tqdm(f, total=n_lines):
            yield line


def pbar_file_generator(dir_):
    sizecounter = 0
    for root, dirs, files in os.walk(dir_):
        for fname in files:
            filepath = os.path.join(root, fname)
            sizecounter += os.stat(filepath).st_size

    with tqdm(total=sizecounter,
              unit='B', unit_scale=True, unit_divisor=1024) as pbar:

        for root, dirs, files in os.walk(dir_):
            for fname in files:
                filepath = os.path.join(root, fname)
                yield filepath

                pbar.set_postfix(file=fname, refresh=False)
                pbar.update(os.stat(filepath).st_size)

