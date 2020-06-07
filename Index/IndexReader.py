"""---------------------------------------------------------------------------------------------------------------------
Dassi Krakinovski:  318525920
Naama Swimmer:      318754066
---------------------------------------------------------------------------------------------------------------------"""
import struct
import os
import re
review_len = 24


class IndexReader:
    string = ""
    dictionary = bytes(0)
    reviews = b''
    pl = b''
    dir = ""
    """Creates an IndexReader which will read from the given directory"""
    def __init__(self, dir):
        with open(f"{dir}//string_file.txt", "r") as str_file:
            self.string = str_file.read()
        with open(f"{dir}//dict_file.bin","br") as dict_file:
            self.dictionary = dict_file.read()
        with open(f"{dir}//reviews.bin", "br") as reviews_file:
            self.reviews = reviews_file.read()
        self.dir = dir

    """Returns the product identifier for the given review Returns null if there is no review with the given identifier"""
    def getProductId(self,reviewId):
        if reviewId>0 and reviewId<= self.getNumberOfReviews():
            product_id = self.reviews[(reviewId-1)*review_len:(reviewId-1)*review_len+10]
            if product_id != b'':
                return product_id.decode()
        return None

    """Returns the score for a given review Returns -1 if there is no review with the given identifier"""
    def getReviewScore(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            score = self.reviews[(reviewId-1)*review_len+10:(reviewId-1)*review_len+11]
            if score != b'':
                return ord(score)
        return -1

    """Returns the numerator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessNumerator(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            numerator = self.reviews[(reviewId - 1) * review_len + 12:(reviewId - 1) * review_len + 16]  #TODO: there is an empty byte before those ints...
            if numerator != b'':
                return struct.unpack("i", numerator)[0]
        return -1

    """Returns the denominator for the helpfulness of a given review Returns -1 if there is no review with the given identifier"""
    def getReviewHelpfulnessDenominator(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            denomirator = self.reviews[(reviewId - 1) * review_len + 16:(reviewId - 1) * review_len + 20]  #TODO: there is an empty byte before those ints...
            if denomirator != b'':
                return struct.unpack("i", denomirator)[0]
        return -1

    """Returns the number of tokens in a given review Returns -1 if there is no review with the given identifier"""
    def getReviewLength(self, reviewId):
        if reviewId > 0 and reviewId <= self.getNumberOfReviews():
            len = self.reviews[(reviewId - 1) * review_len + 20:(reviewId - 1) * review_len + 24]  # TODO: there is an empty byte before those ints...
            if len != b'':
                return struct.unpack("i", len)[0]
        return -1

    """Return the number of reviews containing a given token (i.e., word) Returns 0 if there are no reviews containing this token"""
    def getTokenFrequency(self, token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        self.uncompress_pl(letter, pl_offset, pl_next_offset)
        if pl_offset == -1:
            return 0
        return pl_next_offset - pl_offset

    """Return the number of times that a given token (i.e., word) appears in the reviews indexed 
       Returns 0 if there are no reviews containing this token"""
    def getTokenCollectionFrequency(self,token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        if pl_offset == -1:
            return 0
        count_tokens = 0
        with open(f"{self.dir}//pl_{letter}.bin", "br") as pl_file:
            self.pl = pl_file.read()
        for i in range(pl_offset, pl_next_offset):
            count_tokens += struct.unpack("i" ,self.pl[i*8+4:i*8+8])[0]
        return count_tokens

    """Returns a series of integers (Tupple) of the form id-1, freq-1, id-2, freq-2, ... such that id-n is the n-th review containing the given token and freq-n is the number of times that the token appears in review id-n 
        Note that the integers should be sorted by id 
       Returns an empty Tupple if there are no reviews containing this token"""
    def getReviewsWithToken(self, token):
        if type(token) != str:
            return 0
        token = self.normalize(token)
        pl_offset, pl_next_offset, letter = self.pl_offset(token)
        pl_tuple = []
        if pl_offset == -1:
            return tuple(pl_tuple)
        with open(f"{self.dir}//pl_{letter}.bin", "br") as pl_file:
            self.pl = pl_file.read()
        for i in range(pl_offset, pl_next_offset):
            pl_tuple.append(struct.unpack("i", self.pl[i * 8:i * 8 + 4])[0])
            pl_tuple.append(struct.unpack("i" ,self.pl[i * 8+4:i*8+8])[0])
        return tuple(pl_tuple)

    """Return the number of product reviews available in the system"""
    def getNumberOfReviews(self):
        size_review = len(self.reviews)
        return size_review//24

    """Return the number of tokens in the system (Tokens should be counted as many times as they appear)"""
    def getTokenSizeOfReviews(self):
        count_tokens = 0
        for i in range(0, self.getNumberOfReviews()):
            count_tokens += struct.unpack("i",self.reviews[i*review_len+20:i*review_len+24])[0]
        return count_tokens


    """Return the ids of the reviews for a given product identifier Note that the integers returned should be sorted by id Returns an empty Tuple if there are no reviews for this product"""
    def getProductReviews(self, productId):
        reviews_id = []
        for i in range(1, self.getNumberOfReviews()):
            if self.getProductId(i) == productId:
                reviews_id.append(i)
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
        size = os.stat(f"{self.dir}//pl_{letter}.bin").st_size
        if pl_next_offset == 0:
            pl_next_offset = size // 8
        return pl_offset, pl_next_offset, letter

    def uncompress_pl(self, pl, pl_offset, pl_next_offset):
        with open(f"{self.dir}//pl_{pl}.bin", "br") as pl_file:
            pl_buff = b''
            pl_file.seek(pl_offset)
            pl_buff = pl_file.read(pl_next_offset-pl_offset)
            print(pl_buff)
        i = 0
        num_bytes = [1, 1, 1, 1]
        posting_list = []
        while i < len(pl_buff):
            #print()
            byte = pl_buff[i] #int.from_bytes(pl_buff[i].to_bytes(1, byteorder='little'), byteorder="little")
            #print(byte)
            num_bytes[0] = (byte & 192) >> 6
            num_bytes[1] = (byte & 48) >> 4
            num_bytes[2] = (byte & 12) >> 2
            num_bytes[3] = byte & 3
            print(num_bytes)
            i += 1
            prev_byte = i
            for num in num_bytes:
                print(f"prev {prev_byte} num {num}")
                print(pl_buff[i])
                print(int.from_bytes(pl_buff[1:1], byteorder="little"))
                posting_list.append(int.from_bytes(pl_buff[prev_byte:prev_byte+num], byteorder="little"))
                prev_byte += num
            i += 4
        print(posting_list)

    def normalize(self, token):
        token = token.lower()
        token = token.strip()
        return token

r = IndexReader("dir")
print(r.getTokenFrequency("a"))