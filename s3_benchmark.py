#!/usr/bin/env python

import sys
import os
from tqdm import tqdm
import time
import numpy as np


def download(mount_point, max_size):
    # Change current working directory to the mount_point
    os.chdir(mount_point)

    # Calculate the range in bytes to download
    range_end = max_size - 1  # Range is zero-based, so end at max_size - 1
    range_header = f"Range: bytes=0-{range_end}"

    result = os.system(
        f'wget --header="{range_header}" https://uhhpc.herts.ac.uk/~mjh/test.tar -O partial_test.tar')
    if result != 0:
        raise RuntimeError('Download failed!')

    result = os.system('tar xvf partial_test.tar')
    if result != 0:
        raise RuntimeError('Untar failed!')


if __name__ == '__main__':
    print('Running toy DP3 benchmark')

    # Check if the mount point is provided as an argument
    try:
        mount_point = sys.argv[1]
    except IndexError:
        print('Usage: DP3_benchmark.py <mount_point> [operation]')
        raise

    # Change working directory to the mount point
    os.chdir(mount_point)

    # Determine the operation, defaulting to 'benchmark' if not specified
    operation = sys.argv[2] if len(sys.argv) > 2 else 'benchmark'

    if operation not in ['download', 'benchmark']:
        raise RuntimeError(f'Unknown operation {operation} specified')

    print(f'Running operation {operation}')

    max_size = 21 * 1024 * 1024 * 1024  # Set max download size to 20GB

    if operation == 'download':
        download(mount_point, max_size)
    elif operation == 'benchmark':
        if not os.path.isdir('test.ms'):
            download(mount_point, max_size)
        times = []
        count = 5
        for i in tqdm(range(count)):
            os.system('rm -r test2.ms')
            st = time.time()
            os.system(
                'DP3 numthreads=8 msin=test.ms msout=test2.ms steps=[ave] msin.datacolumn=DATA msout.datacolumn=DATA ave.type=averager ave.freqstep=8')
            et = time.time()
            times.append(et - st)
        print('Average execution time %f seconds' % np.mean(times))
        print('Max execution time %f seconds' % np.max(times))
        print('Std dev of execution time %f seconds' % np.std(times))
