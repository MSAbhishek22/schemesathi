"""Tests for SchemeSathi core engine (parser + explainable matcher).

Run from ~/workspace/hackathons/slay-hacks:
    python3 -m unittest discover -s tests -v

Linux run receipt — see RELEASE_CARD.md for the recorded pass count.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app"))

from schemes import parse_profile, profile_from_form, match_all, evaluate, SCHEMES, what_if


def verdicts(profile):
    return {r["scheme"]["id"]: r["verdict"] for r in match_all(profile)}


class TestParser(unittest.TestCase):
    def test_student_sentence(self):
        p = parse_profile("I am a 19 year old student from Meerut, Uttar Pradesh. "
                          "My family income is 2 lakh per year. I want a scholarship for college.")
        self.assertEqual(p["age"], 19)
        self.assertEqual(p["annual_income"], 200000)
        self.assertEqual(p["state"], "Uttar Pradesh")
        self.assertIn("student", p["occupations"])

    def test_farmer_hinglish(self):
        p = parse_profile("I am a 45 year old kisan from a village. I own 2 acres of land. "
                          "Family income 1.5 lakh per year.")
        self.assertEqual(p["age"], 45)
        self.assertEqual(p["annual_income"], 150000)
        self.assertIn("farmer", p["occupations"])
        self.assertIn("landholding", p["flags"])
        self.assertIn("rural", p["flags"])

    def test_income_bare_rupees(self):
        p = parse_profile("my family income is 50000")
        self.assertEqual(p["annual_income"], 50000)

    def test_income_monthly_annualised(self):
        p = parse_profile("I earn 20000 per month")
        self.assertEqual(p["annual_income"], 240000)

    def test_income_crore(self):
        p = parse_profile("family income 1 crore per year")
        self.assertEqual(p["annual_income"], 10000000)

    def test_no_false_sc_flag_from_school(self):
        # "school" contains "sc" — must NOT set the SC/ST flag.
        p = parse_profile("I am a student in school, age 16")
        self.assertNotIn("sc_st", p["flags"])

    def test_no_false_senior_from_70000(self):
        # "70000" contains "70" — must NOT set the senior70 flag.
        p = parse_profile("my income is 70000, I am 30 years old")
        self.assertNotIn("senior70", p["flags"])
        self.assertEqual(p["age"], 30)

    def test_senior_age_sets_flag(self):
        p = parse_profile("I am 72 years old")
        self.assertIn("senior70", p["flags"])

    def test_daughter_sentence(self):
        p = parse_profile("My daughter is 7 years old. I want to save for her education.")
        self.assertEqual(p["age"], 7)
        self.assertEqual(p["gender"], "female")
        self.assertIn("girl_child", p["flags"])

    def test_vendor_thela(self):
        p = parse_profile("I sell vegetables from a thela in Delhi")
        self.assertIn("vendor", p["occupations"])
        self.assertIn("street_vendor", p["flags"])
        self.assertEqual(p["state"], "Delhi")

    def test_empty_text_never_raises(self):
        p = parse_profile("")
        self.assertIsNone(p["age"])
        self.assertEqual(p["occupations"], set())

    def test_garbage_text_never_raises(self):
        p = parse_profile("!!! ??? 12345 hello")
        # A bare number with no income keyword and no ₹ is not trusted.
        self.assertIsNone(p["annual_income"])


class TestMatcher(unittest.TestCase):
    def test_student_low_income_matches(self):
        v = verdicts(profile_from_form({
            "age": "19", "annual_income": "200000", "gender": "female",
            "occupation": "student", "sc_st": True, "post_matric": True}))
        self.assertEqual(v["post-matric-sc"], "ELIGIBLE")
        self.assertEqual(v["pmjdy"], "ELIGIBLE")

    def test_farmer_matches_kisan_and_fasal(self):
        v = verdicts(profile_from_form({
            "age": "45", "annual_income": "150000", "occupation": "farmer",
            "landholding": True, "rural": True}))
        self.assertEqual(v["pm-kisan"], "ELIGIBLE")
        self.assertEqual(v["pmfby"], "ELIGIBLE")

    def test_close_on_income_just_over_cap(self):
        # Post-matric SC caps at 2.5 lakh; 3 lakh is 20% over -> CLOSE.
        v = verdicts(profile_from_form({
            "age": "19", "annual_income": "300000", "gender": "female",
            "occupation": "student", "sc_st": True, "post_matric": True}))
        self.assertEqual(v["post-matric-sc"], "CLOSE")

    def test_hard_no_on_income_way_over_cap(self):
        # 10 lakh vs 2.5 lakh cap is 4x over -> NOT ELIGIBLE, not CLOSE.
        v = verdicts(profile_from_form({
            "age": "19", "annual_income": "1000000", "gender": "female",
            "occupation": "student", "sc_st": True, "post_matric": True}))
        self.assertEqual(v["post-matric-sc"], "NOT ELIGIBLE")

    def test_needs_info_when_income_missing(self):
        v = verdicts(profile_from_form({
            "age": "19", "occupation": "student", "sc_st": True,
            "post_matric": True}))
        self.assertEqual(v["post-matric-sc"], "NEEDS INFO")

    def test_senior_70_gets_vaya_vandana(self):
        v = verdicts(profile_from_form({"age": "72"}))
        self.assertEqual(v["vaya-vandana"], "ELIGIBLE")

    def test_girl_child_7_gets_sukanya(self):
        v = verdicts(profile_from_form({
            "age": "7", "gender": "female", "girl_child": True}))
        self.assertEqual(v["sukanya"], "ELIGIBLE")

    def test_girl_child_12_too_old_for_sukanya(self):
        v = verdicts(profile_from_form({
            "age": "12", "gender": "female", "girl_child": True}))
        self.assertEqual(v["sukanya"], "NOT ELIGIBLE")

    def test_vendor_gets_svanidhi(self):
        v = verdicts(profile_from_form({
            "age": "32", "annual_income": "250000", "occupation": "vendor",
            "street_vendor": True, "urban": True}))
        self.assertEqual(v["svanidhi"], "ELIGIBLE")

    def test_what_if_income_drop_opens_scheme(self):
        base = profile_from_form({
            "age": "19", "annual_income": "300000", "gender": "female",
            "occupation": "student", "sc_st": True, "post_matric": True})
        before = verdicts(base)["post-matric-sc"]
        after = {r["scheme"]["id"]: r["verdict"]
                 for r in what_if(base, annual_income=200000)}["post-matric-sc"]
        self.assertEqual(before, "CLOSE")
        self.assertEqual(after, "ELIGIBLE")

    def test_every_scheme_has_docs_steps_benefit(self):
        for s in SCHEMES:
            self.assertTrue(s["docs"], s["id"])
            self.assertTrue(s["steps"], s["id"])
            self.assertTrue(s["benefit"], s["id"])
            self.assertTrue(s["ministry"], s["id"])

    def test_trace_explains_every_verdict(self):
        p = profile_from_form({"age": "19", "annual_income": "200000",
                               "occupation": "student"})
        for r in match_all(p):
            self.assertTrue(r["checks"], r["scheme"]["id"])
            for c in r["checks"]:
                self.assertIn(c["passed"], (True, False, None))
                self.assertTrue(c["label"])
                self.assertTrue(c["detail"])

    def test_apy_age_window(self):
        self.assertEqual(verdicts(profile_from_form(
            {"age": "25", "occupation": "unemployed"}))["apy"], "ELIGIBLE")
        self.assertEqual(verdicts(profile_from_form(
            {"age": "45", "occupation": "unemployed"}))["apy"], "NOT ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
