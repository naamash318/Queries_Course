"""---------------------------------------------------------------------------------------------------------------------
Dassi Krakinovski:  318525920
Naama Swimmer:      318754066
---------------------------------------------------------------------------------------------------------------------"""
import struct
import os
from datetime import datetime
import re
review_len = 21


class IndexReader:
    string = ""
    dictionary = bytes(0)
    reviews = b''
    pl = b''
    dir = ""
    tokens_count = 0
    reviews_count = 0
    """Creates an IndexReader which will read from the given directory"""
    def __init__(self, dir):
        with open(f"{dir}//string_file.txt", "r") as str_file:
            self.string = str_file.read()
        with open(f"{dir}//dict_file.bin","br") as dict_file:
            self.dictionary = dict_file.read()
        with open(f"{dir}//general.txt", 'r') as general_file:
            self.reviews_count = int(general_file.readline())
            self.tokens_count = int(general_file.readline())
        # with open(f"{dir}//reviews.bin", "br") as reviews_file:
        #     self.reviews = reviews_file.read()
        self.dir = dir

    """Returns the product identifier for the given review Returns null if there is no review with the given identifier"""
    def getProductId(self,reviewId):
        if reviewId>0 and reviewId<= self.getNumberOfReviews():
            review = self.return_review(reviewId)
            product_id = review[0:10]
            if product_id != b'':
                return product_id.decode()
        return None

    """Returns the score for a given review Returns -1 if there is no review with the given identifier"""
    def getReviewScore(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            review = self.return_review(reviewId)
            score = review[10:11]
            if score != b'':
                return ord(score)
        return -1

    """Returns the numerator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessNumerator(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            review = self.return_review(reviewId)
            numerator = review[11:15]
            if numerator != b'':
                return int.from_bytes(numerator, byteorder="little")
        return -1

    """Returns the denominator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessDenominator(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            review = self.return_review(reviewId)
            denomirator = review[15:19]
            if denomirator != b'':
                return int.from_bytes(denomirator, byteorder="little")
        return -1

    """Returns the number of tokens in a given review Returns -1 if there is no review with the given identifier"""
    def getReviewLength(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            review = self.return_review(reviewId)
            len = review[19:21]
            if len != b'':
                return int.from_bytes(len, byteorder="little")
        return -1

    """Return the number of reviews containing a given token (i.e., word) Returns 0 if there are no reviews containing this token"""
    def getTokenFrequency(self, token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        if pl_offset == -1:
            return 0
        pl = self.uncompress_pl(letter, pl_offset, pl_next_offset)
        return len(pl)//2

    """Return the number of times that a given token (i.e., word) appears in the reviews indexed 
       Returns 0 if there are no reviews containing this token"""
    def getTokenCollectionFrequency(self,token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        if pl_offset == -1:
            return 0
        pl = self.uncompress_pl(letter, pl_offset, pl_next_offset)
        count_tokens = 0
        i = 1
        while i < len(pl):
            count_tokens += pl[i]
            i += 2
        return count_tokens

    """Returns a series of integers (Tupple) of the form id-1, freq-1, id-2, freq-2, ... such that id-n is the n-th review containing the given token and freq-n is the number of times that the token appears in review id-n 
        Note that the integers should be sorted by id 
       Returns an empty Tupple if there are no reviews containing this token"""
    def getReviewsWithToken(self, token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        if pl_offset == -1:
            return ()
        pl = self.uncompress_pl(letter, pl_offset, pl_next_offset)
        return tuple(pl)

    """Return the number of product reviews available in the system"""
    def getNumberOfReviews(self):
        # size_review = os.stat(f"{self.dir}//reviews.bin").st_size
        # return size_review//review_len
        return self.reviews_count

    """Return the number of tokens in the system (Tokens should be counted as many times as they appear)"""
    def getTokenSizeOfReviews(self):
        # count_tokens = 0
        # with open(f"{self.dir}//reviews.bin", 'br') as review_file:
        #     reviews = review_file.read()
        # for i in range(0, self.getNumberOfReviews()):
        #     count_tokens += int.from_bytes(reviews[i*review_len+19:i*review_len+21], byteorder="little")
        return self.tokens_count


    """Return the ids of the reviews for a given product identifier Note that the integers returned should be sorted by id Returns an empty Tuple if there are no reviews for this product"""
    def getProductReviews(self, productId):
        reviews_id = []
        with open(f"{self.dir}//reviews.bin", 'br') as review_file:
             reviews = review_file.read()
        for i in range(0, self.getNumberOfReviews()):
            if reviews[i*review_len:i*review_len+10].decode() == productId:
                reviews_id.append(i+1)
        return tuple(reviews_id)


    def binary_search(self, word):
        right = len(self.dictionary)//8
        left = 0
        while left <= right:
            mid = (left + right) // 2
            loc = struct.unpack("i",self.dictionary[mid*8:mid*8+4])[0]
            next_loc = struct.unpack("i",self.dictionary[mid*8+8:mid*8+12])[0]
            if self.string[loc:next_loc] == word:
                return True, mid
            elif self.string[loc:next_loc] < word:  # string appears before word
                left = mid + 1
            else:
                right = mid - 1
        return False, right


    def pl_offset(self, token):
        exist, loc = self.binary_search(token)
        if not exist:
            return -1, -1, "-1"
        letter = token[0]
        if letter >= 'a':
            letter = ord(letter) - 87
        pl_offset = struct.unpack("i", self.dictionary[loc*8+4:loc*8+8])[0]
        pl_next_offset = struct.unpack("i", self.dictionary[loc*8+12:loc*8+16])[0]

        return pl_offset, pl_next_offset, letter


    def uncompress_pl(self, pl, pl_offset, pl_next_offset):
        with open(f"{self.dir}//pl_{pl}.bin", "br") as pl_file:
            pl_file.seek(pl_offset)
            if pl_next_offset == 0:
                pl_buff = pl_file.read()
            else:
                pl_buff = pl_file.read(pl_next_offset-pl_offset)
        i = 0
        num_bytes = [1, 1, 1, 1]
        posting_list = []
        while i < len(pl_buff):
            byte = pl_buff[i]
            num_bytes[0] = (byte & 192) >> 6
            num_bytes[1] = (byte & 48) >> 4
            num_bytes[2] = (byte & 12) >> 2
            num_bytes[3] = byte & 3
            i += 1
            prev_byte = i
            j = 0
            for num in num_bytes:
                posting_list.append(int.from_bytes(pl_buff[prev_byte + j:prev_byte + j + num + 1], byteorder="little"))
                prev_byte += num
                j += 1
                i += 1+num
        posting_list = self.calc_difference(posting_list)
        return posting_list

    def calc_difference(self, pl):
        i = 2
        while i <= len(pl)-1:
            if pl[i] == 0:
                j = i
                while j <= len(pl):
                    pl.remove(0)
                    j += 1
                break;
            pl[i] = pl[i] + pl[i-2]
            i += 2
        return pl

    def return_review(self, reviewId):
        with open(f"{self.dir}//reviews.bin", "br") as reviews_file:
            reviews_file.seek((reviewId-1)*review_len)
            review = reviews_file.read(review_len)
        return review


    def normalize(self, token):
        token = token.lower()
        token = token.strip()
        return token

# r = IndexReader("my_dir")
# print(r.getTokenFrequency("commercialization"))
# print(r.getTokenCollectionFrequency("commercialization"))
# print(r.getReviewsWithToken("commercialization"))
# # print(r.getProductId(99))
# # print(r.getReviewScore(99))
# # print(r.getReviewHelpfulnessNumerator(1))
# print(r.getTokenSizeOfReviews())
# print(r.getNumberOfReviews())
# # print(r.getProductReviews("0312322291"))
