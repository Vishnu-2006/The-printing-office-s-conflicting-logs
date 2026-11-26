# PrintFlow — Printing Office Queue Consolidator

A full-stack Flask web application for Problem Statement 04. It merges already-sorted department job queues into one deterministic timeline using a custom linked list and custom min heap.

## Features
- Multiple department queues (up to 200) and up to 100,000 jobs.
- Custom singly linked queue and custom binary min heap.
- Stable tie rule: timestamp ascending, then department code alphabetically (case-insensitive), then original index within that department.
- Input validation, empty queues, duplicate timestamps and uneven queue sizes.
- Merge report, responsive dashboard, CSV export and SQLite merge history.
- REST endpoints: `GET /api/health`, `POST /api/merge`, `GET /api/history`.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended):
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start: `python run.py`
6. Open http://127.0.0.1:5000

## Input JSON format
```json
{
  "departments": [
    {"code": "A", "jobs": [{"id": "A2", "time": 2}, {"id": "A7", "time": 7}]},
    {"code": "B", "jobs": [{"id": "B1", "time": 1}]}
  ]
}
```
Each department's queue must already be sorted by ascending numeric `time`. Department codes must be unique.

## Algorithm
- Each department is stored in a linked queue.
- The first job of every non-empty queue is inserted into the custom min heap.
- Repeatedly extract the minimum job, append it to the final timeline, then insert the next job from that same department.
- Heap priority is `(timestamp, department code, original index)`.

Time complexity: **O(N log K)**; auxiliary merge storage: **O(K)** excluding input queues and output timeline. `N` is total jobs; `K` is number of departments.

## Test
Run from the project root:
```bash
python -m unittest discover -s tests -v
```

## Notes
- No printer hardware connection is included, as the problem statement says it is not required.
- SQLite history is stored in `instance/printing_office.sqlite3`.
