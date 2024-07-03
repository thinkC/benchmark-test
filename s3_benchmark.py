import sys
import os
import subprocess
from tqdm import tqdm
import time
import numpy as np

def download_file(url, output_dir):
    """
    Download a file from a URL and save it to the specified directory.
    
    Parameters:
    - url (str): The URL of the file to download.
    - output_dir (str): The directory where the file will be saved.
    
    Raises:
    - RuntimeError: If the download or extraction fails.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
        
        # Download the file
        download_command = f'wget {url}'
        result = os.system(download_command)
        if result != 0:
            raise RuntimeError(f'Download failed for URL: {url}')
        
        # Extract the file (assuming it's a tar archive)
        filename = url.split('/')[-1]
        extract_command = f'tar xvf {filename}'
        result = os.system(extract_command)
        if result != 0:
            raise RuntimeError(f'Extraction failed for file: {filename}')
        
    except Exception as e:
        raise RuntimeError(f'Failed to download and extract file: {e}')

def mount_s3_bucket(bucket_name, mount_point, passwd_file):
    """
    Mount an S3 bucket using s3fs to a specified directory.
    
    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - mount_point (str): The directory where the S3 bucket will be mounted.
    - passwd_file (str): The path to the file containing S3 credentials.
    
    Raises:
    - RuntimeError: If the mount operation fails.
    """
    try:
        os.makedirs(mount_point, exist_ok=True)
        mount_command = f's3fs {bucket_name} {mount_point} -o passwd_file={passwd_file} -o url=https://enno.openstack.com -o endpoint=enno.openstack.com -o use_path_request_style'
        result = os.system(mount_command)
        if result != 0:
            raise RuntimeError(f'Failed to mount S3 bucket: {bucket_name}')
        
    except Exception as e:
        raise RuntimeError(f'Failed to mount S3 bucket: {e}')

def benchmark_operation(executable_path, operation_args):
    """
    Run a benchmarking operation using an executable file.
    
    Parameters:
    - executable_path (str): The path to the executable file.
    - operation_args (list): List of arguments to pass to the executable.
    
    Returns:
    - list: List of execution times for each operation run.
    """
    try:
        times = []
        count = 5
        
        for i in tqdm(range(count), desc='Benchmarking'):
            subprocess.run(operation_args, check=True)
            times.append(time.time())
        
        return times
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Benchmark operation failed: {e}')

if __name__ == '__main__':
    try:
        # Check command-line arguments
        if len(sys.argv) != 4:
            print('Usage: python DP3_benchmark.py <temp_dir> <mount_point> <operation>')
            sys.exit(1)
        
        temp_dir = sys.argv[1]
        mount_point = sys.argv[2]
        operation = sys.argv[3]
        
        # Mount S3 bucket
        mount_s3_bucket('user-bucket01', mount_point, '/home/rocky/.passwd-s3fs')
        
        # Download file
        download_file('https://uhhpc.herts.ac.uk/~mjh/test.tar', temp_dir)
        
        # Change working directory to temp_dir
        os.chdir(temp_dir)
        
        # Perform benchmark operation
        if operation == 'benchmark':
            executable_path = 'DP3'  # Assuming DP3 is an executable or a command
            times = benchmark_operation(executable_path, ['numthreads=8', 'msin=test.ms', 'msout=test2.ms', 'steps=[ave]', 'msin.datacolumn=DATA', 'msout.datacolumn=DATA', 'ave.type=averager', 'ave.freqstep=8'])
            print('Benchmark results:')
            print(f'Average execution time: {np.mean(times)} seconds')
            print(f'Max execution time: {np.max(times)} seconds')
            print(f'Std dev of execution time: {np.std(times)} seconds')
        else:
            print(f'Unknown operation: {operation}')
            sys.exit(1)
    
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
