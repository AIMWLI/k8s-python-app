from concurrent.futures import ThreadPoolExecutor, as_completed

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="worker")


def run_tasks(tasks):
    futures = {_executor.submit(fn, *args): name for name, fn, args in tasks}
    results = {}
    for f in as_completed(futures):
        name = futures[f]
        try:
            results[name] = f.result()
        except Exception as e:
            results[name] = str(e)
    return results


def shutdown():
    _executor.shutdown(wait=True)
