
class IndexReader
    def __init__(self, dir):
    """Creates an IndexReader which will read from the given directory"""


    def getProductId(self,
                 reviewId): """Returns the product identifier for the given review Returns null if there is no review with the given identifier"""


    def getReviewScore(self,
                   reviewId): """Returns the score for a given review Returns -1 if there is no review with the given identifier"""


    def getReviewHelpfulnessNumerator(self,
                                  reviewId): """Returns the numerator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""


    def getReviewHelpfulnessDenominator(self,
                                    reviewId): """Returns the denominator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""


    def getReviewLength(self,
                        reviewId): """Returns the number of tokens in a given review Returns -1 if there is no review with the given identifier"""


    def getTokenFrequency(self,
                          token): """Return the number of reviews containing a given token (i.e., word) Returns 0 if there are no reviews containing this token"""


    def getTokenCollectionFrequency(self,
                                    token): """Return the number of times that a given token (i.e., word) appears in the reviews indexed Returns 0 if there are no reviews containing this token"""


    def getReviewsWithToken(self, token): """Returns a series of integers (Tupple) of the form id-1, freq-1, id-2, freq-2, ... such that id-n is the n-th review containing the given token and freq-n is the number of times that the token appears in review id-n Note that the integers should be sorted by id 
    
    Returns an empty Tupple if there are no reviews containing this token"""


    def getNumberOfReviews(self): """Return the number of product reviews available in the system"""


    def getTokenSizeOfReviews(
            self): """Return the number of tokens in the system (Tokens should be counted as many times as they appear)"""


    def getProductReviews(self,
                          productId): """Return the ids of the reviews for a given product identifier Note that the integers returned should be sorted by id Returns an empty Tuple if there are no reviews for this product"""