import unittest
import sys
from metadata_extractor import MetadataExtractor

class TestExtractMethods(unittest.TestCase):
    def setUp(self):
        self.wat = "test_files/test.wat"
        self.html = "test_files/test.html"
        self.extractor = MetadataExtractor()

    def test_extract_wat(self):
        d = self.extractor.extract_data_from_wat(self.wat)
        data = {'publisher': 'The Verge', 'publisherCountry': u'US', 'author': 'Chris Welch', 'url': 'https://www.theverge.com/2018/1/22/16921102/google-breaks-amazon-fire-tv-youtube-workaround', 'publisherCoordinates': '25.7743,-80.1937', 'publishedDate': '2018-01-22T17:34:03-05:00', 'title': 'Google briefly broke Amazon\xe2\x80\x99s workaround for YouTube on Fire TV', 'header': 'Fire TV owners can no longer access the TV-friendly YouTube interface in a web browser.', 'modifiedDate': '2018-01-22T17:34:03-05:00'}

        self.assertEqual(d,data)

    def test_extract_html(self):
        d = self.extractor.extract_data_from_html(self.html)
        data = {'publisher': 'latimes.com', 'publisherCountry': u'US', 'author': 'Sergei L. Loiko', 'url': 'http://www.latimes.com/world/worldnow/la-fg-wn-crimea-referendum-date-20140301-story.html', 'publisherCoordinates': '47.6062,-122.3321', 'publishedDate': '2014-03-01T04:36:00-0800', 'title': 'New Crimea leaders move up referendum date', 'header': "KIEV, Ukraine -- Crimea's new pro-Moscow premier, Sergei Aksenov, moved the date of the peninsula's status referendum to March 30.", 'modifiedDate': '2014-03-01T04:36:43-0800'}

        self.assertEqual(d,data)


if __name__ == '__main__':
    unittest.main()
