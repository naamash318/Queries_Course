import struct
review_len = 24


class IndexReader:
    string = ""
    dictionary = bytes(0)
    reviews = b''
    """Creates an IndexReader which will read from the given directory"""
    def __init__(self, dir):
        with open(f"{dir}//string_file.txt","r") as str_file:
            self.string = str_file.read()
        with open(f"{dir}//dict_file.bin","br") as dict_file:
            self.dictionary = dict_file.read()
        with open(f"{dir}//reviews.bin", "br") as reviews_file:
            self.reviews = reviews_file.read()

    """Returns the product identifier for the given review Returns null if there is no review with the given identifier"""
    def getProductId(self,reviewId):
        product_id = self.reviews[(reviewId-1)*review_len:(reviewId-1)*review_len+10]
        if product_id != b'':
            return product_id.decode()
        return None

    """Returns the score for a given review Returns -1 if there is no review with the given identifier"""
    def getReviewScore(self, reviewId):
        score = self.reviews[(reviewId-1)*review_len+10:(reviewId-1)*review_len+11]
        if score != b'':
            return ord(score)
        return -1

    """Returns the numerator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessNumerator(self, reviewId):
        numerator = self.reviews[(reviewId - 1) * review_len + 12:(reviewId - 1) * review_len + 16]  #TODO: there is an empty byte before those ints...
        if numerator != b'':
            return struct.unpack("i", numerator)[0]
        return -1

    """Returns the denominator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessDenominator(self, reviewId):
        denomirator = self.reviews[(reviewId - 1) * review_len + 16:(reviewId - 1) * review_len + 20]  #TODO: there is an empty byte before those ints...
        if denomirator != b'':
            return struct.unpack("i", denomirator)[0]
        return -1

    """Returns the number of tokens in a given review Returns -1 if there is no review with the given identifier"""
    def getReviewLength(self, reviewId):
        len = self.reviews[(reviewId - 1) * review_len + 20:(reviewId - 1) * review_len + 24]  # TODO: there is an empty byte before those ints...
        if len != b'':
            return struct.unpack("i", len)[0]
        return -1

    """Return the number of reviews containing a given token (i.e., word) Returns 0 if there are no reviews containing this token"""
    def getTokenFrequency(self, token):
        exist, loc = self.binary_search(token)
        if not exist:
            return 0
        letter = token[0]
        pl_offset = self.dictionary[loc*8+4:loc*8+8]
        print(f"{exist} {loc}")

    def getTokenCollectionFrequency(self,
                                    token): """Return the number of times that a given token (i.e., word) appears in the reviews indexed Returns 0 if there are no reviews containing this token"""


    def getReviewsWithToken(self, token): """Returns a series of integers (Tupple) of the form id-1, freq-1, id-2, freq-2, ... such that id-n is the n-th review containing the given token and freq-n is the number of times that the token appears in review id-n Note that the integers should be sorted by id 
    
    Returns an empty Tupple if there are no reviews containing this token"""


    def getNumberOfReviews(self): """Return the number of product reviews available in the system"""


    def getTokenSizeOfReviews(
            self): """Return the number of tokens in the system (Tokens should be counted as many times as they appear)"""


    def getProductReviews(self,
                          productId): """Return the ids of the reviews for a given product identifier Note that the integers returned should be sorted by id Returns an empty Tuple if there are no reviews for this product"""

    def binary_search(self, word):
        right = len(self.dictionary)//8
        left = 0
        while left <= right:
            mid = (left + right) // 2
            loc = struct.unpack("i",self.dictionary[mid*8:mid*8+4])[0]
            next_loc = struct.unpack("i",self.dictionary[mid*8+8:mid*8+12])[0]
            #print(f"mid is {mid} string[{loc}:{next_loc}] is {self.string[loc:next_loc]}")
            if self.string[loc:next_loc] == word:
                return True, mid
            elif self.string[loc:next_loc] < word:  # string appears before word
                print("in plus")
                left = mid + 1
            else:
                right = mid - 1
        return False, right

r = IndexReader("dir")
print(r.getProductId(3))
print(r.getReviewScore(3))
print(r.getReviewHelpfulnessNumerator(3))
print(r.getReviewHelpfulnessDenominator(3))
print(r.getReviewLength(3))
print(r.getTokenFrequency("ab"))