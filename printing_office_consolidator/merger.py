"""Validation and k-way merge implementation."""
from .structures import Job, LinkedQueue, MinHeap

MAX_DEPARTMENTS = 200
MAX_JOBS = 100_000


class InputError(ValueError):
    pass


def build_queues(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("departments"), list):
        raise InputError("Request must contain a 'departments' array.")

    departments = payload["departments"]
    if len(departments) > MAX_DEPARTMENTS:
        raise InputError(f"Maximum supported departments: {MAX_DEPARTMENTS}.")

    seen_codes = set()
    total = 0
    queues = []
    input_view = []

    for dept in departments:
        if not isinstance(dept, dict):
            raise InputError("Each department must be an object.")
        code = str(dept.get("code", "")).strip()
        if not code:
            raise InputError("Every department needs a non-empty code.")
        normalized = code.casefold()
        if normalized in seen_codes:
            raise InputError(f"Department code '{code}' is repeated.")
        seen_codes.add(normalized)

        jobs_data = dept.get("jobs", [])
        if not isinstance(jobs_data, list):
            raise InputError(f"Jobs for department {code} must be an array.")

        queue = LinkedQueue()
        display_jobs = []
        previous_time = None
        for index, raw in enumerate(jobs_data):
            if not isinstance(raw, dict):
                raise InputError(f"Every job in department {code} must be an object.")
            job_id = str(raw.get("id", "")).strip()
            if not job_id:
                raise InputError(f"A job in department {code} is missing its ID.")
            try:
                timestamp = float(raw["time"])
            except (KeyError, TypeError, ValueError):
                raise InputError(f"Job {job_id} in {code} needs a numeric time.")
            if timestamp != timestamp or timestamp in (float("inf"), float("-inf")):
                raise InputError(f"Job {job_id} in {code} has an invalid time.")
            if previous_time is not None and timestamp < previous_time:
                raise InputError(f"Queue {code} is not ordered by submission time.")
            previous_time = timestamp
            job = Job(job_id, timestamp, code, index)
            queue.append(job)
            display_jobs.append(job.as_dict())
            total += 1
            if total > MAX_JOBS:
                raise InputError(f"Maximum supported jobs: {MAX_JOBS}.")
        queues.append((code, queue))
        input_view.append({"code": code, "jobs": display_jobs})

    return queues, input_view, total


def merge_departments(payload):
    queues, input_view, received = build_queues(payload)
    heap = MinHeap()

    # Keep a direct reference to each linked queue for O(1) next-job access.
    queue_map = {code: queue for code, queue in queues}

    # Only the first job from each department is initially inserted.
    for code, queue in queues:
        if queue.peek() is not None:
            heap.push(queue.pop())

    merged = []
    while len(heap):
        job = heap.pop()
        merged.append(job.as_dict())

        # Locate the linked queue for this department and add its next job.
        # A queue map keeps this lookup O(1).
        next_job = queue_map[job.department].pop()
        if next_job is not None:
            heap.push(next_job)

    return {
        "input_queues": input_view,
        "timeline": merged,
        "report": {
            "departments_received": len(queues),
            "jobs_received": received,
            "jobs_produced": len(merged),
            "jobs_missing": received - len(merged),
            "empty_departments": sum(1 for _, q in queues if len(q) == 0),
            "status": "success" if received == len(merged) else "error",
            "complexity": "O(N log K)",
        },
    }
