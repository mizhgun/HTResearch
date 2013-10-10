from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from nltk.stem.porter import PorterStemmer
from scrapy.http import TextResponse
import math
from ..items import *
import pdb
import re

# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.


class ContactPositionScraper:

    def __init__(self):
        position = ""


class ContactPublicationsScraper:

    def __init__(self):
        publications = []


class EmailScraper:
    def parse(self, response):
        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+\[at][A-Za-z0-9.-]+\[dot][A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+ dot [A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\(dot\)[A-Za-z]{2,4}\b')
        hxs = HtmlXPathSelector(response)

        # body will get emails that are just text in the body
        body = hxs.select('//body').re(email_regex)
        
        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(email_regex)
        
        emails = body+hrefs

        # Take out the unicode or whatever, and substitute [at] for @ and [dot] for .
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii','ignore')
            emails[i] = re.sub(r'(\[at]|\(at\)| at )([A-Za-z0-9.-]+)(\[dot]|\(dot\)| dot )', r'@\2.', emails[i])

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        # Make the list an item
        email_list = []
        for email in emails:
            item = ScrapedEmail()
            item['email'] = email
            email_list.append(item)

        return email_list


class IndianPhoneNumberScraper:
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        india_format_regex = re.compile(r'\b(?!\s)(?:91[-./\s]+)?[0-9]+[0-9]+[-./\s]?[0-9]?[0-9]?[-./\s]?[0-9]?[-./\s]?[0-9]{5}[0-9]?\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(india_format_regex)

        phone_nums = body 

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            item = ScrapedPhoneNumber()
            item['phone_number'] = num
            phone_nums_list.append(item)

        return phone_nums_list


class NameScraper:

    def __init__(self):
        names = []


class OrgAddressScraper:

    def __init__(self):
        addresses = []


class OrgContactsScraper:

    def __init__(self):
        contacts = []

class OrgUrlScraper:

    def __init__(self):
        url = []

class OrgPartnersScraper:

    def __init__(self):
        partners = []


class OrgTypeScraper:
    
    def __init__(self):

        self._type_count = 3
        self._stemmer = PorterStemmer()
        self._stopwords = [ 'a', 'a\'s', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after', 'afterwards', 'again', 'against', 'ain\'t', 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', 'aren\'t', 'around', 'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'b', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 'c', 'c\'mon', 'c\'s', 'came', 'can', 'can\'t', 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', 'couldn\'t', 'course', 'currently', 'd', 'definitely', 'described', 'despite', 'did', 'didn\'t', 'different', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'done', 'down', 'downwards', 'during', 'e', 'each', 'edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'f', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'g', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'h', 'had', 'hadn\'t', 'happens', 'hardly', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'s', 'hello', 'help', 'hence', 'her', 'here', 'here\'s', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'ie', 'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 'instead', 'into', 'inward', 'is', 'isn\'t', 'it', 'it\'d', 'it\'ll', 'it\'s', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'knows', 'known', 'l', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'let\'s', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'm', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself', 'n', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'o', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'p', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'q', 'que', 'quite', 'qv', 'r', 'rather', 'rd', 're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 's', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she', 'should', 'shouldn\'t', 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 't', 't\'s', 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'that\'s', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'there\'s', 'thereafter', 'thereby', 'therefore', 'therein', 'theres', 'thereupon', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two', 'u', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'uucp', 'v', 'value', 'various', 'very', 'via', 'viz', 'vs', 'w', 'want', 'wants', 'was', 'wasn\'t', 'way', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'welcome', 'well', 'went', 'were', 'weren\'t', 'what', 'what\'s', 'whatever', 'when', 'whence', 'whenever', 'where', 'where\'s', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'who\'s', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'won\'t', 'wonder', 'would', 'would', 'wouldn\'t', 'x', 'y', 'yes', 'yet', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves', 'z', 'zero' ]
        self._org_terms = {
            'education': [
                'education',
                'school',
                'study',
                'teach',
            ],
            'religious': [
                'religious',
                'God',
                'worship',
                'church',
                'spiritual',
            ],
            'advocacy': [
                'lobbying',
                'policy',
                'legal',
                'media',
                'change',
                'government',
                'state',
                'court',
            ],
            'government': [
                'government',
                'act',
                'nation',
                'state',
                'department',
                'united',
                'investigation',
                'intervention',
                'legislation',
                'agency',
                'court',
                'bill',
                'committee',
                'law',
                'enforcement',
                'legal',
                'conviction',
                'ministry',
                'secretary',
                'agency',
            ],
            'research': [
                'research',
                'conduct',
                'documentation',
                'study',
                'identify',
                'analysis',
                'understand',
                'find',
                'insight',
                'link',
                'correlation',
                'compile',
                'report',
                'data',
                'publication',
                'book',
                'journal',
                'periodical',
                'newsletter',
            ],
            'prevention': [
                'prevention',
                'intervention',
                'education',
                'development',
                'community',
                'ownership',
            ],
            'protection': [
                'protection',
                'rescue',
                'rehabilitation',
                'reintegration',
                'repatriation',
                'empowerment',
                'repatriation',
                'fulfilment',
                'freedom',
                'opportunity',
            ],
            'prosecution': [
                'prosecution',
                'compliance',
                'abolish',
                'law',
                'enforcement',
                'regulatory',
            ],
        }

        # List of document term lists
        self._documents = []

    # Stem word, converting to lowercase
    def _stem(self, word):
        return self._stemmer.stem(word).lower()
    
    # Load document and get terms
    def _load_document(self, response):
        html = response.body_as_unicode() #'<p>This is some <a href="http://www.google.com/">text</a> Sam\'s #50 school! study; "God...spiritual; worship/religious"</p>'
            
        # Get unique word stems from plain text
        text = html2text.html2text(html)
        text = re.sub("[^a-zA-Z']+", ' ', text)
        docTerms = text.split()
        docTerms = [ token.strip("'") for token in docTerms ]
        docTerms = [ self._stem(token) for token in docTerms ]
        docTerms = [ token for token in docTerms if token not in self._stopwords ]

        # Add new set of terms to list of document term lists
        self._documents.append(docTerms)

        return docTerms

    # Dot product of two vectors
    def _dot(self, arr1, arr2):
        return sum([ arr1[i] * arr2[i] for i in range(min(len(arr1), len(arr2))) ])
    
    # length of a vector, i.e. ||v||
    def _norm(self, arr):
        return math.sqrt(sum([item * item for item in arr]))
    
    # Cosine of two vectors, used for matching query terms
    def _cosine(self, arr1, arr2):
        dot = self._dot(arr1, arr2)
        norms = self._norm(arr1) * self._norm(arr2)
        return float((dot / norms) if norms > 0 else 0)
    
    # Index terms in a list of tokens in a document
    def _index_terms(self, tokens):
        uniqueTokens = list(set(tokens))
        vectorKeywordIndex = {}
        for i in range(len(uniqueTokens)):
            vectorKeywordIndex[uniqueTokens[i]] = i
        return vectorKeywordIndex
    
    #####
    # tf-idf (term frequency - inverse document frequency) model for mapping document string to vector
    #####

    # raw frequency of a term in a document
    def _freq(self, term, docTerms):
        return docTerms.count(term)
    
    # maximum frequency of any term in a document
    def _max_freq(self, docTerms):
        return docTerms.count(max(set(docTerms), key=docTerms.count))

    # term frequency - measure of how common a term is in a document
    def _tf(self, term, docTerms):
        rawFreq = self._freq(term, docTerms)
        maxFreq = self._max_freq(docTerms)
        return float(rawFreq) / maxFreq
    
    # inverse document frequency: measure of rarity of term across documents
    def _idf(self, term):
        n = len(self._documents)
        docFreq = 1 + sum(1 for doc in self._documents if term in doc)
        return math.log(1 + n / docFreq)

    # tf-idf
    def _tf_idf(self, term, doc):
        idf = self._idf(term)
        return self._tf(term, doc) * self._idf(term)
    
    # Build vector based on list of terms
    def _build_vector(self, terms, vectorKeywordIndex):
        vector = [0] * len(vectorKeywordIndex)
        for term in vectorKeywordIndex.iterkeys():
            vector[vectorKeywordIndex[term]] = self._tf_idf(term, terms)
        return vector
    
    # Get the organization type
    def parse(self, response):
            
        # Get terms from response
        docTerms = self._load_document(response)
            
        # Make vector index mapping
        vectorKeywordIndex = self._index_terms(docTerms)

        # Build document vector
        docVector = self._build_vector(docTerms, vectorKeywordIndex)
        
        # Find weight of each type
        typeWeights = {}
        for type in self._org_terms:
            # Build query vector
            queryTerms = [ self._stem(token) for token in self._org_terms[type] ]

            queryVector = self._build_vector(queryTerms, vectorKeywordIndex)
                
            # Find the weight from the cosine between the document vector and query vector
            weight = self._cosine(docVector, queryVector)
                
            # set the weight in the type vector
            typeWeights[type] = weight

            # DEBUG
            l = str(len(max(self._org_terms.iterkeys(), key=(lambda key: len(key)))))
            print(('   %' + l + 's: %0.4f') % (type, weight))

        # Get the N (_type_count) highest-weighted matches for organization type
        types = sorted(typeWeights.iterkeys(), key=typeWeights.get, reverse=True)[:self._type_count]

        return types


class PublicationAuthorsScraper:

    def __init__(self):
        authors = []


class PublicationDateScraper:

    def __init__(self):
        partners = []


class PublicationPublisherScraper:

    def __init__(self):
        publisher = []


class PublicationTitleScraper:

    def __init__(self):
        titles = []


class PublicationTypeScraper:

    def __init__(self):
        type = []


class USPhoneNumberScraper:
           
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        us_format_regex = re.compile(r'\b(?! )1?\s?[(-./]?\s?[2-9][0-8][0-9]\s?[)-./]?\s?[2-9][0-9]{2}\s?\W?\s?[0-9]{4}\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(us_format_regex)

        phone_nums = body 

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            item = ScrapedPhoneNumber()
            item['phone_number'] = num
            phone_nums_list.append(item)

        return phone_nums_list
