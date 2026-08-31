import unittest
from unittest.mock import MagicMock, patch

import generate_interests


class GenerateInterestsTests(unittest.TestCase):
    def test_build_headers_looks_like_imdb_web_client(self):
        headers = generate_interests.build_headers("en_US")

        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["accept-language"], "en-US")
        self.assertEqual(headers["content-type"], "application/json")
        self.assertEqual(headers["origin"], "https://www.imdb.com")
        self.assertEqual(headers["referer"], "https://www.imdb.com/")
        self.assertEqual(headers["x-imdb-client-name"], "imdb-web-next-localized")
        self.assertEqual(headers["x-imdb-user-country"], "US")
        self.assertIn("Mozilla/5.0", headers["user-agent"])

    def test_build_headers_defaults_country_when_locale_has_no_region(self):
        headers = generate_interests.build_headers("en")

        self.assertEqual(headers["accept-language"], "en")
        self.assertEqual(headers["x-imdb-user-country"], "US")

    @patch("generate_interests.requests.post")
    def test_fetch_interests_uses_built_headers(self, post_mock):
        response = MagicMock()
        response.json.return_value = {
            "data": {"interestCategories": {"edges": [{"node": {"interests": {"edges": []}}}]}}
        }
        post_mock.return_value = response
        expected_headers = generate_interests.build_headers()

        result = generate_interests.fetch_interests(retries=1)

        self.assertEqual(result, [{"node": {"interests": {"edges": []}}}])
        post_mock.assert_called_once_with(
            generate_interests.GRAPHQL_URL,
            headers=expected_headers,
            json={"query": generate_interests.QUERY},
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
