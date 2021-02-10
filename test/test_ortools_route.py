import unittest

from hypothesis import given, strategies as st, settings

import ortools_route


class RouteTestCase(unittest.TestCase):
    @settings(deadline=None, max_examples=1000)
    @given(st.lists(st.tuples(st.floats(min_value=-180, max_value=180), st.floats(min_value=-180, max_value=180)), min_size=4), st.booleans())
    def test_recalc(self, old_route, arbitrary_ends):
        new_route = ortools_route.recalc_routecalc(old_route, arbitrary_ends)
        self.assertEqual(sorted(new_route), sorted(old_route))
