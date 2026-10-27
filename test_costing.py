import csv
import io
import unittest
from decimal import Decimal
from costing import csv_bytes, die_cost, material_cost, money, summarize


class CostTests(unittest.TestCase):
    def test_material_percentage_and_units(self):
        self.assertEqual(material_cost(100, 120, 5), Decimal("12.60"))

    def test_round_half_up(self):
        self.assertEqual(money("1.005"), Decimal("1.01"))

    def test_die_boundaries_and_missing(self):
        rules = [{"最大邊長上限 (mm)": 50, "穴數": 2, "每件壓鑄費 (NT$)": 3},
                 {"最大邊長上限 (mm)": 100, "穴數": 2, "每件壓鑄費 (NT$)": 5}]
        self.assertEqual(die_cost([50, 10, 20], 2, rules), Decimal("3.00"))
        self.assertEqual(die_cost([50.01, 10, 20], 2, rules), Decimal("5.00"))
        self.assertIsNone(die_cost([101, 10, 20], 2, rules))
        self.assertIsNone(die_cost([50, 10, 20], 4, rules))
        self.assertIsNone(die_cost([0, 10, 20], 2, rules))

    def test_summary_zero_and_reconciliation(self):
        total, rows = summarize([("原料", 0), ("其他", 0)])
        self.assertEqual(total, 0)
        self.assertEqual(rows[0]["佔比 (%)"], 0)
        total, rows = summarize([("原料", "1.005"), ("其他", "2.005")])
        self.assertEqual(total, Decimal("3.02"))
        self.assertAlmostEqual(sum(r["佔比 (%)"] for r in rows), 100)

    def test_invalid_values(self):
        for value in [-1, "NaN", "Infinity"]:
            with self.assertRaises(ValueError):
                money(value)

    def test_csv_roundtrip_and_formula_escape(self):
        result = csv_bytes([["案件,名稱", '中文\n第二行', '=1+1', ' @SUM(A1)', '12.60']])
        self.assertTrue(result.startswith(b'\xef\xbb\xbf'))
        row = next(csv.reader(io.StringIO(result.decode("utf-8-sig"))))
        self.assertEqual(row, ["案件,名稱", '中文\n第二行', "'=1+1", "' @SUM(A1)", '12.60'])


if __name__ == "__main__":
    unittest.main()
