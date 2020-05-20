import SlowIndexWriter
import IndexReader
import unittest
import re
import time

class test(unittest.TestCase):

    #def test_index_build(self):

        #S = SlowIndexWriter.SlowIndexWriter("reviews//review1.txt", "dir")

    def test_product_id(self):
        r = IndexReader.IndexReader("dir")

        #print("---------------------Test getProductId-------------------------")
        prod_id = r.getProductId(20000000)
        self.assertEqual(prod_id,None, f"incorrect prod id {prod_id} for review 20000000")
        prod_id = r.getProductId(-1)
        self.assertEqual(prod_id,None,f'incorrect prod id {prod_id} for review -1')
        prod_id = r.getProductId(0)
        self.assertEqual(prod_id,None,f'incorrect prod id {prod_id} for review 0')
        prod_id = r.getProductId(1)
        self.assertEqual(prod_id,'1882931173',f'incorrect prod id {prod_id} for review 1')
        prod_id = r.getProductId(1000)
        self.assertEqual(prod_id,'0882899228',f'incorrect prod id {prod_id} for review 1000')

    def test_score(self):
        r = IndexReader.IndexReader("dir")
        for i in range(1,10):
            score = r.getReviewScore(i)
            self.assertTrue(score>=0 and score<=5,f"incorrect score for review {i}")
        self.assertEqual(r.getReviewScore(0),-1,"incoorect score for review 0")
        self.assertEqual(r.getReviewScore(100000), -1, "incoorect score for review 1000000")
        self.assertEqual(r.getReviewScore(-7), -1, "incoorect score for review 0")

    def test_helpfulness(self):
        r = IndexReader.IndexReader("dir")
        for i in range(1,101):
            n = r.getReviewHelpfulnessNumerator(i)
            d = r.getReviewHelpfulnessDenominator(i)
            self.assertTrue(n>=0 and d>=0 and n<=d,f"incorrect helpfulness {n}/{d} for review {i}")
        self.assertEqual(r.getReviewHelpfulnessNumerator(0),-1,"incoorect helpfulness for review 0")
        self.assertEqual(r.getReviewHelpfulnessNumerator(100000), -1, "incoorect helpfulness for review 1000000")
        self.assertEqual(r.getReviewHelpfulnessNumerator(-7), -1, "incoorect helpfulness for review 0")
        self.assertEqual(r.getReviewHelpfulnessDenominator(0), -1, "incoorect helpfulness for review 0")
        self.assertEqual(r.getReviewHelpfulnessDenominator(100000), -1, "incoorect helpfulness for review 1000000")
        self.assertEqual(r.getReviewHelpfulnessDenominator(-7), -1, "incoorect helpfulness for review 0")

    def test_score(self):
        r = IndexReader.IndexReader("dir")
        for i in range(1, 1001):
            len = r.getReviewLength(i)
            self.assertTrue(len >= 0, f"incorrect length for review {i}")
        self.assertEqual(r.getReviewLength(0), -1, "incoorect length for review 0")
        self.assertEqual(r.getReviewLength(100000), -1, "incoorect length for review 1000000")
        self.assertEqual(r.getReviewLength(-7), -1, "incoorect length for review 0")

    def test_token_freq(self):
        r = IndexReader.IndexReader("dir")
        with open("reviews/Books100.txt") as books:
            words = books.read()
        words = re.split(r'[_\b\W]+', words)
        #for word in words:
           # if word != '':
           #     self.assertNotEqual(r.getTokenFrequency(word), 0, f'error {word}')

        self.assertEqual(r.getTokenFrequency('about/80'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('ABout'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency(' about '), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('a'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('you'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), 0, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), 0, "error")
        self.assertEqual(r.getTokenFrequency('wsdfgtke'),0,"error")

    def test_collec_freq(self):
        r = IndexReader.IndexReader("dir")
        with open("reviews/Books100.txt") as books:
            words = books.read()
        #words = re.split(r'[_\b\W]+', words)
       # for word in words:
        #    if word != '':
         #       self.assertNotEqual(r.getTokenCollectionFrequency(word), 0, f'error {word}')

        self.assertNotEqual(r.getTokenCollectionFrequency('about'), 0, "error")
        self.assertNotEqual(r.getTokenCollectionFrequency('ABout'), 0, "error")
        self.assertNotEqual(r.getTokenCollectionFrequency(' about '), 0, "error")
        self.assertEqual(r.getTokenCollectionFrequency('wsdfgtke'),0,"error")

    def test_get_reviews_with_token(self):
        r = IndexReader.IndexReader("dir")
        self.assertEqual(r.getReviewsWithToken('wsdfgtke'), (), "error")

    # def test_get_num_of_reviews(self):
    #
    #     print("try 100")
    #     S = SlowIndexWriter.SlowIndexWriter("reviews//Books100.txt", "dir")
    #     r = IndexReader.IndexReader("dir")
    #     self.assertEqual(r.getNumberOfReviews(), 100, "error 100")
    #     S.removeIndex("dir")
    #
    #     #time.sleep(100)
    #     print("try 1000")
    #     S = SlowIndexWriter.SlowIndexWriter("reviews//Books1000.txt", "dir1")
    #     r = IndexReader.IndexReader("dir1")
    #     self.assertEqual(r.getNumberOfReviews(), 1000, "error 1000")
    #     S.removeIndex("dir1")
    #
    #     print("try review1")
    #     S = SlowIndexWriter.SlowIndexWriter("reviews//review1.txt", "dir")
    #     r = IndexReader.IndexReader("dir")
    #     self.assertEqual(r.getNumberOfReviews(), 1, "error 1")
    #     S.removeIndex("dir")

    def test_get_num_of_tokens(self):
        print("try 100")
        #S = SlowIndexWriter.SlowIndexWriter("reviews//Books10.txt", "dir")
        r = IndexReader.IndexReader("dir")
        print(f'test {r.getTokenSizeOfReviews()}')
        #S.removeIndex("dir")
    #
    #     # time.sleep(100)
    #     print("try 1000")
    #     S = SlowIndexWriter.SlowIndexWriter("reviews//Books1000.txt", "dir1")
    #     r = IndexReader.IndexReader("dir1")
    #     self.assertNotEqual(r.getTokenSizeOfReviews(), 1000, "error 1000")
    #     S.removeIndex("dir1")
    #
    # def test_get_product_review(self):
    #     S = SlowIndexWriter.SlowIndexWriter("reviews//Books100.txt", "dir")
    #     r = IndexReader.IndexReader("dir")
    #
    #     self.assertEqual(r.getProductReviews('0'), (), "error")
    #     self.assertNotEqual(r.getProductReviews('B000NKGYMK'), (), "error")


    # print(r.getProductId(100))
    # print(r.getReviewScore(100))
    # print(r.getReviewHelpfulnessNumerator(100))
    # print(r.getReviewHelpfulnessDenominator(100))
    # print(r.getReviewLength(100))
    # print(r.getTokenFrequency("About"))
    # print(r.getTokenCollectionFrequency("abOUt"))
    # print(r.getReviewsWithToken("about      "))
    # print(r.getNumberOfReviews())
    # print(r.getTokenSizeOfReviews())
    # print(r.getProductReviews("B000NKGYMK"))

if __name__=="__main__":
    S = SlowIndexWriter.SlowIndexWriter("reviews//Books1000.txt", "dir")
    unittest.main()
