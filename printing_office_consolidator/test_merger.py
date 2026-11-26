import unittest
from app.merger import merge_departments, InputError


class MergeTests(unittest.TestCase):
    def test_illustrative_example(self):
        result = merge_departments({"departments": [
            {"code":"A","jobs":[{"id":"A2","time":2},{"id":"A7","time":7},{"id":"A9","time":9}]},
            {"code":"B","jobs":[{"id":"B1","time":1},{"id":"B7","time":7}]},
            {"code":"C","jobs":[{"id":"C3","time":3},{"id":"C10","time":10}]},
        ]})
        self.assertEqual([j["job_id"] for j in result["timeline"]],
                         ["B1","A2","C3","A7","B7","A9","C10"])

    def test_tie_by_department_then_stable_order(self):
        result = merge_departments({"departments": [
            {"code":"B","jobs":[{"id":"B1","time":5},{"id":"B2","time":5}]},
            {"code":"A","jobs":[{"id":"A1","time":5},{"id":"A2","time":5}]},
        ]})
        self.assertEqual([j["job_id"] for j in result["timeline"]],
                         ["A1","A2","B1","B2"])

    def test_empty_queues_and_all_empty(self):
        result = merge_departments({"departments":[
            {"code":"A","jobs":[]},{"code":"B","jobs":[{"id":"B1","time":1}]}
        ]})
        self.assertEqual(len(result["timeline"]),1)
        self.assertEqual(result["report"]["jobs_missing"],0)
        empty = merge_departments({"departments":[{"code":"A","jobs":[]}]})
        self.assertEqual(empty["timeline"],[])

    def test_reject_unsorted_queue(self):
        with self.assertRaises(InputError):
            merge_departments({"departments":[{"code":"A","jobs":[
                {"id":"A2","time":2},{"id":"A1","time":1}
            ]}]})

    def test_duplicate_department(self):
        with self.assertRaises(InputError):
            merge_departments({"departments":[{"code":"A","jobs":[]},{"code":"a","jobs":[]}]})

if __name__ == "__main__":
    unittest.main()
