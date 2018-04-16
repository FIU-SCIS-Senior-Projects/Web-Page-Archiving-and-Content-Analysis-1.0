import unittest
import sys
import content_extractor as ex
from bs4 import BeautifulSoup


def make_soup(html_string):
    return BeautifulSoup(html_string, 'lxml')


def nodes_to_str(node_list):
    return [str(n) for n in node_list]


class TestExtractorUtils(unittest.TestCase):
    def test_inner_html(self):
        soup = make_soup('<html><body><p>child</p></body></html>')
        self.assertEqual(ex.inner_html(
            soup), '<html><body><p>child</p></body></html>')

    def test_get_children_with_content(self):
        soup = make_soup('<body><p>child</p></body>')
        child = ex.get_children(soup.body)
        self.assertEqual(nodes_to_str(child), ['<p>child</p>'])

    def test_get_children_with_no_content(self):
        child = ex.get_children(None)
        self.assertEqual(child, [])

    def test_get_ancestors(self):
        soup = make_soup('<body><p><a>Deep</a></p></body>')
        ancestors = ex.get_ancestors(soup.find('a'), 2)
        ancestors_strs = nodes_to_str(ancestors)
        self.assertEquals(
            ancestors_strs, ['<p><a>Deep</a></p>', '<body><p><a>Deep</a></p></body>'])

    def test_has_single_p_inside_element(self):
        soup = make_soup(
            "<body><div id='parent'><p>Single P</p></div></body>")
        parent = soup.find(attrs={'id': 'parent'})
        self.assertTrue(ex.has_single_p_inside_element(parent))

    def test_has_single_p_inside_element_with_non_extra_element(self):
        soup = make_soup(
            "<body><div id='parent'><div><p>Single P</p></div></div></body>")
        parent = soup.find(attrs={'id': 'parent'})
        self.assertFalse(ex.has_single_p_inside_element(parent))

    def test_has_single_p_inside_element_with_non_extra_p(self):
        soup = make_soup(
            "<body><div id='parent'><p>One P</p><p>Two P</p></div></body>")
        parent = soup.find(attrs={'id': 'parent'})
        self.assertFalse(ex.has_single_p_inside_element(parent))

    def test_has_child_block_elements(self):
        soup = make_soup("<body><a>block yes</a></body>")
        self.assertTrue(ex.has_child_block_elements(soup.body))

    def test_has_child_block_elements_with_no_block_els(self):
        soup = make_soup("<body><span>block yes</span></body>")
        self.assertFalse(ex.has_child_block_elements(soup.body))

    def test_is_empty_candidate(self):
        soup = make_soup("<body><div>Yes Candidate</div></body>")
        self.assertTrue(ex.is_empty_candidate(soup.find('div')))

    def test_is_empty_candidate_not_candidate(self):
        soup = make_soup("<body><a>Not Candidate</a></body>")
        self.assertFalse(ex.is_empty_candidate(soup.find('a')))

    def test_is_element_without_content(self):
        soup = make_soup("<body></body>").body
        soup2 = make_soup("<body><br/><hr/></body>").body
        self.assertTrue(ex.is_element_without_content(soup))
        self.assertTrue(ex.is_element_without_content(soup2))

    def test_remove_and_get_next(self):
        soup = make_soup("<body><p>root</p><a>next</a></body>").body
        root = soup.p
        nxt = ex.remove_and_get_next(root)
        self.assertEqual(str(nxt), '<a>next</a>')
        self.assertEqual(str(soup), '<body><a>next</a></body>')

    def test_get_next_node(self):
        soup = make_soup(
            "<body><p><span>Next In</span></p><a>next sibl</a></body>").body
        root = soup.p
        nxt = ex.get_next_node(root)
        self.assertEqual(str(nxt), '<span>Next In</span>')

    def test_get_next_node_finish_depth_first(self):
        soup = make_soup(
            "<body><p><span>Next In<br /></span></p><a>next sibl</a></body>").body
        root = soup.br
        nxt = ex.get_next_node(root)
        self.assertEqual(str(nxt), '<a>next sibl</a>')

    def test_get_next_node_ignore_self_kids(self):
        soup = make_soup(
            "<body><p><span>Next In</span></p><a>next sibl</a></body>").body
        root = soup.p
        nxt = ex.get_next_node(root, True)
        self.assertEqual(str(nxt), '<a>next sibl</a>')

    def test_get_class_name(self):
        soup = make_soup(
            '<body><p class="one">root</p><a>next</a></body>').body
        soup2 = make_soup(
            '<body><p class="one two">root</p><a>next</a></body>').body
        self.assertEqual(ex.get_class_name(soup.p), 'one')
        self.assertEqual(ex.get_class_name(soup2.p), 'one two')

    def test_get_class_name_no_class(self):
        soup = make_soup('<body><p>root</p><a>next</a></body>').body
        self.assertEqual(ex.get_class_name(soup.p), '')

    def test_get_id_str(self):
        soup = make_soup(
            '<body><p id="one">root</p><a>next</a></body>').body
        self.assertEqual(ex.get_id_str(soup.p), 'one')

    def test_get_id_str_no_id(self):
        soup = make_soup('<body><p>root</p><a>next</a></body>').body
        self.assertEqual(ex.get_id_str(soup.p), '')

    def test_get_role_attr(self):
        soup = make_soup(
            '<body><p role="one">root</p><a>next</a></body>').body
        self.assertEqual(ex.get_role_attr(soup.p), 'one')

    def test_get_role_attr_no_role(self):
        soup = make_soup('<body><p>root</p><a>next</a></body>').body
        self.assertEqual(ex.get_role_attr(soup.p), '')

    def test_is_tag(self):
        soup = make_soup('<body>Hello</body>').body
        self.assertTrue(ex.is_tag(soup))

    def test_is_tag_with_non_tag(self):
        self.assertFalse(ex.is_tag("not tag"))

    def test_first_element_child(self):
        soup = make_soup('<body><p>root</p><a>next</a></body>').body
        child = ex.first_element_child(soup)
        self.assertEqual(str(child), '<p>root</p>')

    def test_first_element_child_with_non_tags_near(self):
        soup = make_soup('<body>Floating text <a>next</a></body>').body
        child = ex.first_element_child(soup)
        self.assertEqual(str(child), '<a>next</a>')

    def test_first_element_child_no_child(self):
        soup = make_soup('<body></body>').body
        child = ex.first_element_child(soup)
        self.assertEqual(child, False)

    def test_next_element_sibling(self):
        soup = make_soup('<body><p>root</p><a>next</a></body>').body
        root = soup.p
        sibl = ex.next_element_sibling(root)
        self.assertEqual(str(sibl), '<a>next</a>')

    def test_next_element_sibling_with_non_tags_near(self):
        soup = make_soup(
            '<body><p>root</p>Floating text <a>next</a></body>').body
        root = soup.p
        sibl = ex.next_element_sibling(root)
        self.assertEqual(str(sibl), '<a>next</a>')

    def test_next_element_sibling_no_sibl(self):
        soup = make_soup('<body><p>root</p></body>').body
        root = soup.p
        sibl = ex.next_element_sibling(root)
        self.assertEqual(sibl, False)


"""
Integration Tests
"""


class TestContentUtils(unittest.TestCase):
    def setUp(self):
        self.html = "test_files/test.html"
        self.invalid = "test_files/invalid.html"
        self.contrivedHtml = "test_files/simple.html"
        self.real_life_content = u'\nKIEV, Ukraine -- Crimea\'s new pro-Moscow premier, Sergei Aksenov, moved the date of the peninsula\'s status referendum to March 30.On Thursday, the Crimean parliament, which appointed Aksenov,\xa0 had called for a referendum on May 25, the date also set for the urgent presidential election in Ukraine.\u201cIn connection with a necessity we decided to speed up the holding of the referendum on the stauts of the Autonomous Republic of the Crimea,\u201d Aksenov said Saturday in Simferopol at a new government session, the UNIAN information agency reported.Earlier that day, Aksenov, head of the nationalist Russian Unity organization, appealed to Russian President Vladimir Putin \u201cto render assistance in securing peace and tranquility on the territory of the Autonomous Republic of the Crimea," UNIAN reported.\nMentioning some curious \u201cdisorders with use of firearms,\u201d Aksenov assumed \u201ctemporary\u201d command over Ukraine\'s law enforcement structures, army and navy units stationed in the Crimea.By law the police, army and navy are subordinated directly to Kiev.Aksenov acknowledged Saturday that Russian troops were protecting key sites in Crimea.\u201cWe have established cooperation with the Black Sea Fleet in protecting the important assets,\u201d Aksenov said in televised remarks. \u201cI am sure they can carry out tasks to protect public order.\u201d\nEarlier this week,\xa0Aksenov organized a pro-Russia rally in front of the parliament in Simferopol, at the same location and time when the Crimean Tatar community held their protest rally. A\xa0 confrontation led to clashes resulting in two dead and 35 injured.On Thursday, unidentified gunmen, believed to be Russian commandos, captured government buildings in Simferopol including the regional parliament, where shortly an urgent session was held behind closed doors. Lawmakers fired the previous government and appointed Aksenov head of the new one.In the last regional legislature elections in 2010, the Russian nationalists headed by Aksenov gained only three seats in the 100-seat regional parliament.On Saturday, Aksenov also made an unprecedented and illegitimate move by assuming personal control over all law enforcement structures, army and navy units stationed in Ukraine. Those who would obey the new order and serve under his command should quit the service, Aksenov said.Heavily armed Russian military patrolling streets in the center of Simferopol still surround the government building and city airport, free-lance journalist Alexander Mnakatsanyan said\u201cAt about 12:30 [p.m.] a group of masked gunmen broke the the door of Ukraine customs section in the aiport and rushed in,\u201d Mnakatsanyan said in a phone interview from Simferopol. \u201cThere were screams and shouts inside and sounds of commotion but no shooting. Ukraine police stationed inside the airport building didn\'t interfere.\u201dThe interim government in Kiev said they won\'t fall for provocations and compared the presence of Russian troops in Ukraine with Russian troops invading South Ossetia during the brief war between Russia and Georgia in 2008. Two Georgian breakaway republics \u2013 South Ossetia and Ablhazia \u2013 assisted by the Russian military then declared independence, which was immediately recognized by Russia and a handful of other countries.\u201cThe presence of the Russian troops [in the Crimea] is a provocation, and we demand that the Russian military immediately return to their bases of regular deployment,\u201d Ukraine Prime Minister Arseny Yatsenyuk said Saturday in televised remarks opening an urgent session of the new Cabinet.\u201cRussian partners, stop provoking a civil confrontation in Ukraine and observe the basic agreements between Ukraine and the Russian Federation.\u201dUkraine will do its best to preserve its territorial integrity, Yatsenyuk said.Russia is acting cynically and ruthlessly but it still tries to shroud its actions in some semblance of legitimacy, political scientist Igor Popov said.\u201cNow it is becoming clear they needed to rescue [ousted President Victor] Yanukovich and have him under Moscow\'s protection to attach legitimacy to their actions,\u201d Popov, head of the Politika Analytical Center, a Kiev-based think tank, said in an interview with The Times.\u201cThe Kremlin keeps saying that Yanukovich is still Ukraine\'s legitimate president and as such he endorsed the setting up of Moscow\'s puppet government in the Crimea, which in turn begs Moscow for assistance\u201d.The new Crimean government is trying to hold a referendum on the status of the peninsula as soon as possible while Russian troops are still there and Kiev and Washington can\'t figure out how to get them out.sergei.loiko@latimes.com'

    def test_parse(self):
        content = ex.parse(self.contrivedHtml)
        self.assertEqual(
            content, u'\nMy First Heading Test paragraph\nTesting lost text Single p content good to go some quote i another My first paragraph. ')

    def test_parse_invalid_file(self):
        content = ex.parse(self.invalid)
        self.assertIsNone(content)

    def test_real_file(self):
        self.assertAlmostEqual(ex.parse(self.html), self.real_life_content)


if __name__ == '__main__':
    unittest.main()
    # tests_to_run = [TestExtractorUtils]

    # loader = unittest.TestLoader()

    # suites = []
    # for test_class in tests_to_run:
    #     suite = loader.loadTestsFromTestCase(test_class)
    #     suites.append(suite)

    # all_suites = unittest.TestSuite(suites)

    # runner = unittest.TextTestRunner()
