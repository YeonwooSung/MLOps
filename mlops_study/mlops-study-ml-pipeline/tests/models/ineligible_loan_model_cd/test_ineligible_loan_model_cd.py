import unittest


class TestIneligibleLoanModelCd(unittest.TestCase):
    def test_get_next_branch(self):
        import models.ineligible_loan_model_cd.ineligible_loan_model_cd as model
        next_branch = model.get_next_branch()
        print(f"next_branch = {next_branch}")


if __name__ == '__main__':
    unittest.main()
