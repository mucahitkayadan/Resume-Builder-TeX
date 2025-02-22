import unittest

from parsers.indeed_parser import parse_indeed_job


class TestIndeedParser(unittest.TestCase):

    def test_parse_indeed_job(self):
        url = "https://www.indeed.com/viewjob?jk=example"
        job_description = parse_indeed_job(url)
        self.assertIsInstance(job_description, str)
        self.assertGreater(len(job_description), 0)


if __name__ == "__main__":
    unittest.main()
