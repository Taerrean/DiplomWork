import asyncio
import threading
import multiprocessing
from queue import Queue
from multiprocessing import Pool
import os
import time
import math
import psutil
import aiofiles

# Number of tasks and data for testing
NUM_TASKS = 50
STRINGS = ["Hello World!" for _ in range(NUM_TASKS)]
FACTORIAL_NUMBERS = [100_000 for _ in range(NUM_TASKS)]
FILE_NAME = "test_file.txt"

# Asyncio test functions
async def async_write_file():
    async with aiofiles.open(FILE_NAME, mode='w') as f:
        for string in STRINGS:
            await f.write(string + '\n')

async def async_read_file():
    async with aiofiles.open(FILE_NAME, mode='r') as f:
        await f.read()

async def async_factorial(n):
    return math.factorial(n)

async def asyncio_task():
    await async_write_file()
    await async_read_file()
    await asyncio.gather(*(async_factorial(n) for n in FACTORIAL_NUMBERS))

# Threading test functions
def thread_write_file(queue, lock):
    with lock:
        with open(FILE_NAME, 'w') as f:
            while not queue.empty():
                f.write(queue.get() + '\n')

def thread_read_file(lock):
    with lock:
        with open(FILE_NAME, 'r') as f:
            f.read()

def thread_factorial(n):
    return math.factorial(n)

def threading_task():
    queue = Queue()
    lock = threading.Lock()
    for string in STRINGS:
        queue.put(string)

    writer_thread = threading.Thread(target=thread_write_file, args=(queue, lock))
    reader_thread = threading.Thread(target=thread_read_file, args=(lock,))

    writer_thread.start()
    writer_thread.join()

    reader_thread.start()
    reader_thread.join()

    threads = [threading.Thread(target=thread_factorial, args=(n,)) for n in FACTORIAL_NUMBERS]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

# Multiprocessing test functions
def process_write_file(strings):
    with open(FILE_NAME, 'w') as f:
        for string in strings:
            f.write(string + '\n')

def process_read_file():
    with open(FILE_NAME, 'r') as f:
        f.read()

def process_factorial(n):
    return math.factorial(n)

def multiprocessing_task():
    pool = Pool(processes=4)
    pool.apply(process_write_file, args=(STRINGS,))
    pool.apply(process_read_file)
    pool.map(process_factorial, FACTORIAL_NUMBERS)
    pool.close()
    pool.join()

# CPU and Memory monitoring
def measure_usage(func, *args, **kwargs):
    process = psutil.Process(os.getpid())
    cpu_usage = []
    memory_usage = []

    def monitor():
        while True:
            cpu_usage.append(process.cpu_percent(interval=0.5))
            memory_usage.append(process.memory_info().rss / (1024 * 1024))  # Convert to MB

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()

    avg_cpu = sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0
    avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
    return end_time - start_time, avg_cpu, avg_memory

# Benchmarking
if __name__ == "__main__":
    # Measure asyncio
    asyncio_time, asyncio_cpu, asyncio_memory = measure_usage(asyncio.run, asyncio_task())
    print(f"Asyncio execution time: {asyncio_time:.2f} seconds")
    print(f"Asyncio average CPU usage: {asyncio_cpu:.2f}%")
    print(f"Asyncio average memory usage: {asyncio_memory:.2f} MB")

    # Measure threading
    threading_time, threading_cpu, threading_memory = measure_usage(threading_task)
    print(f"Threading execution time: {threading_time:.2f} seconds")
    print(f"Threading average CPU usage: {threading_cpu:.2f}%")
    print(f"Threading average memory usage: {threading_memory:.2f} MB")

    # Measure multiprocessing
    multiprocessing_time, multiprocessing_cpu, multiprocessing_memory = measure_usage(multiprocessing_task)
    print(f"Multiprocessing execution time: {multiprocessing_time:.2f} seconds")
    print(f"Multiprocessing average CPU usage: {multiprocessing_cpu:.2f}%")
    print(f"Multiprocessing average memory usage: {multiprocessing_memory:.2f} MB")
