[1mdiff --cc HTResearch/WebCrawler/WebCrawler/scrapers/utility_scrapers.py[m
[1mindex 794c602,8a5e66e..0000000[m
[1m--- a/HTResearch/WebCrawler/WebCrawler/scrapers/utility_scrapers.py[m
[1m+++ b/HTResearch/WebCrawler/WebCrawler/scrapers/utility_scrapers.py[m
[1mdiff --cc HTResearch/WebCrawler/WebCrawler/unittests/org_type_scraper_test.py[m
[1mindex f4e12ce,14db4e7..0000000[m
[1m--- a/HTResearch/WebCrawler/WebCrawler/unittests/org_type_scraper_test.py[m
[1m+++ b/HTResearch/WebCrawler/WebCrawler/unittests/org_type_scraper_test.py[m
[1mdiff --cc HTResearch/WebCrawler/WebCrawler/unittests/test_all_scrapers.py[m
[1mindex ec2226e,b80388c..0000000[m
[1m--- a/HTResearch/WebCrawler/WebCrawler/unittests/test_all_scrapers.py[m
[1m+++ b/HTResearch/WebCrawler/WebCrawler/unittests/test_all_scrapers.py[m
[36m@@@ -2,9 -2,7 +2,9 @@@[m [mimport unittes[m
  import pdb[m
  import subprocess[m
  import os[m
[31m -[m
[32m +import subprocess[m
[32m +import json[m
[31m- [m
[32m++import ast[m
  [m
  class ScraperTests(unittest.TestCase):[m
      def test_address_scraper(self):[m
[36m@@@ -76,30 -73,27 +75,47 @@@[m
          for test in assert_list:[m
              self.assertIn(test, keywords, "Keyword " + test + " not found or frequent enough")[m
  [m
[32m +    def test_organization_scraper(self):[m
[32m +        p = subprocess.Popen('scrapy crawl organization_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)[m
[32m +        output, error = p.communicate()[m
[32m +        print(output)[m
[31m-         orgs = json.loads(output)[m
[31m-         assert_list = [[m
[31m-             {[m
[31m-                 'name': 'Bombay Teen Challenge',[m
[31m-                 'types': ['religious'],[m
[31m-                 'phone_number': '+91 22 2604 2242',[m
[31m-                 'email': 'kkdevaraj@bombayteenchallenge.org',[m
[31m-                 'contacts': None,[m
[31m-                 'organization_url': 'https://bombayteenchallenge.org',[m
[31m-                 'partners': None,[m
[31m-             }[m
[31m-         ][m
[32m++        org = ast.literal_eval(output)[m
[32m++        assert_val = {[m
[32m++            'name': 'Bombay Teen Challenge',[m
[32m++            'types': ['religious'],[m
[32m++            'phone_number': '+91 22 2604 2242',[m
[32m++            'email': 'kkdevaraj@bombayteenchallenge.org',[m
[32m++            'contacts': None,[m
[32m++            'organization_url': 'https://bombayteenchallenge.org',[m
[32m++            'partners': None,[m
[32m++        }[m
[32m++[m
[32m++        for attr in assert_val.iterkeys():[m
[32m++            if attr not in org or not org[attr] not in assert_val[attr]:[m
[32m++                match = False[m
[32m++        self.assertTrue(match, 'IT FAILED YOU IDIOT')[m
[32m++[m
[32m+     def test_org_type_scraper(self):[m
[32m+         p = subprocess.Popen('scrapy crawl org_type_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)[m
[32m+         output, error = p.communicate()[m
[32m+         types = output.splitlines()[m
[32m+         types.pop()[m
[32m+ [m
[32m+         assert_list = ['religious', 'government', 'protection'][m
[32m+         for test in assert_list:[m
[32m+             self.assertIn(test, types, 'Type \'' + test + '\' not found')[m
[32m+ [m
[32m+     def test_phone_number_scraper(self):[m
[32m+         # Runs the Test spider and pipes the printed output to "output"[m
[32m+         p = subprocess.Popen('scrapy crawl phone_number_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)[m
[32m+         output, error = p.communicate()[m
[32m+         # Splits the results based on automatically added characters[m
[32m+         numbers = output.splitlines()[m
[32m+         numbers = numbers[:len(numbers)-1][m
  [m
[32m+         assert_list = ["0402026070", "9435134726"][m
          for test in assert_list:[m
[31m-             match = True[m
[31m-             for org in orgs:[m
[31m-                 for attr in test.iterkeys():[m
[31m-                     if attr not in org or not org[attr] not in test[attr]:[m
[31m-                         match = False[m
[31m-             self.assertTrue(match, 'IT FAILED YOU IDIOT')[m
[32m+             self.assertIn(test, numbers, "Phone number " + str(test) + " not found")[m
  [m
  if __name__ == '__main__':[m
      try:[m
[1mdiff --git a/HTResearch/WebCrawler/WebCrawler/scrapers/document_scrapers.py b/HTResearch/WebCrawler/WebCrawler/scrapers/document_scrapers.py[m
[1mindex dce2fc8..2e2fcfe 100644[m
[1m--- a/HTResearch/WebCrawler/WebCrawler/scrapers/document_scrapers.py[m
[1m+++ b/HTResearch/WebCrawler/WebCrawler/scrapers/document_scrapers.py[m
[36m@@ -20,13 +20,9 @@[m [mclass OrganizationScraper:[m
 [m
     def parse(self, response):[m
         organization = ScrapedOrganization()[m
[31m-        print('BEFORE')[m
         for field in self._scrapers.iterkeys():[m
[31m-            print(field)[m
             if self._scrapers[field]:[m
                 organization[field] = self._scrapers[field].parse(response)[m
[31m-                print(organization[field])[m
[31m-        print('AFTER')[m
         return organization[m
 [m
 [m
[1mdiff --git a/HTResearch/WebCrawler/WebCrawler/unittests/organization_scraper_test.py b/HTResearch/WebCrawler/WebCrawler/unittests/organization_scraper_test.py[m
[1mindex 11b12a1..6fa35d1 100644[m
[1m--- a/HTResearch/WebCrawler/WebCrawler/unittests/organization_scraper_test.py[m
[1m+++ b/HTResearch/WebCrawler/WebCrawler/unittests/organization_scraper_test.py[m
[36m@@ -24,10 +24,10 @@[m [mclass OrganizationScraperTest(BaseSpider):[m
                 pass[m
 [m
     def parse(self, response):[m
[31m-        orgs = self.scraper.parse(response)[m
[32m+[m[32m        org = self.scraper.parse(response)[m
         with open("../Output/organization_scraper_output.txt", 'a') as f:[m
[31m-            json_str = json.dumps(orgs)[m
[31m-            f.write(json.dumps(orgs))[m
[31m-            print(json_str)[m
[32m+[m[32m            string = str(org)[m
[32m+[m[32m            f.write(string)[m
[32m+[m[32m            print(string)[m
 [m
[31m-        return orgs[m
[32m+[m[32m        return org[m
