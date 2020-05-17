import SlowIndexWriter
import IndexReader
import unittest

class test(unittest.TestCase):

    def test_index_build(self):
        S = SlowIndexWriter.SlowIndexWriter("reviews//Books1000.txt", "dir")
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
        for i in range(1,1001):
            score = r.getReviewScore(i)
            self.assertTrue(score>=0 and score<=5,f"incorrect score for review {i}")
        self.assertEqual(r.getReviewScore(0),-1,"incoorect score for review 0")
        self.assertEqual(r.getReviewScore(100000), -1, "incoorect score for review 1000000")
        self.assertEqual(r.getReviewScore(-7), -1, "incoorect score for review 0")

    def test_helpfulness(self):
        r = IndexReader.IndexReader("dir")
        for i in range(1,1001):
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
        self.assertNotEqual(r.getTokenFrequency('about'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('ABout'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency(' about '), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('a'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('you'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), -1, "error")
        self.assertNotEqual(r.getTokenFrequency('about'), -1, "error")

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
    unittest.main()
