import re
import os
import struct
import shutil


class SlowIndexWriter:
    reviews_counter = 0
    reviews_buf = bytes(0)
    tokens_list = []
    posting_lists = []
    dictionary = []
    string = ""

    """------------------------------------------------------------------------------------------------------
    Given product review data, creates an on disk index
    inputFile is the path to the file containing the review data
    dir is the directory in which all index files will be created
    if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""
    def __init__(self, inputFile, dir):

        text_file = open(inputFile)
        text = text_file.read()
        start_review = text.find("product/productId: ")
        while start_review != -1:
            end_review = text.find("product/productId: ", start_review+1)
            if self.add_review(text[start_review:end_review])!= 0:
                start_review = end_review
                continue
            self.reviews_counter += 1
            self.add_to_list(text[start_review:end_review])
            start_review=end_review

        self.tokens_list.sort()
        self.create_index()
        self.print_dictionary()
        self.write_index_to_files(dir)




    """מנתחת את הריויו ולוקחת את הפרטים החשובים שומרת את הריויו כאובייקט בינארי (24 בתים) ומוסיפה אתו לבאפר"""
    def add_review(self, review):
        val = ["product/productId: ", "review/helpfulness: ", "review/score: "]
        try:
            # Find product id
            loc = len(val[0])
            product_id = review[loc:loc+10]

            # Find helpfulness
            loc=review.find(val[1])+len(val[1])
            slash_loc = review.find("/", loc)
            end_line = review.find("\n", loc)
            helpfulness_numerator = int(review[loc:slash_loc])   # int = 3 bytes
            helpfulness_denominator = int(review[slash_loc+1:end_line])   # int = 3 bytes

            # find score
            loc = review.find(val[2])+len(val[2])
            end_line = review.find("\n", loc)
            review_score = chr(int(float(review[loc:end_line])))    # 1 byte cnverted from string to float to int t char

            # calculate review len (number of tokens)
            review_len = len(re.split('\W+', review)) - 1   # reduce the token ''

            # pack review data into binary struct
            review_tuple = (product_id.encode('ascii'), review_score.encode(),helpfulness_numerator, helpfulness_denominator, review_len)
            review_format = "10s 1s i i  i"
            s = struct.Struct(review_format)
            packed_data = s.pack(*review_tuple)

            # print("packed review:")
            # print(binascii.hexlify(packed_data))
            # print("size of packed review:")
            # print(s.size)

            self.reviews_buf += packed_data
            print("successfully added review to buf ")
            return 0

        except ValueError as error:
            print("error with review's values")
            return -1

    """מקבלת ריויו מנורמל ויוצרת עבור כל אות רשימה שכל איבר ברשימה הוא טפל של המילה עם מספר המופעים שלה ושולחת את רשימת הרשימות לפונקציה הבאה שתכניס אותם למילון"""
    def add_to_list(self, review):

        review_tokens = self.normalize(review)
        for token in review_tokens:
            if token != '':
                self.tokens_list.append((token, self.reviews_counter))

    def create_index(self):
        count_tokens = 1
        loc_string=0
        loc_posting_list = 0
        num_of_pl = 0
        self.posting_lists.append([])
        for i in range(len(self.tokens_list)):
            if i == len(self.tokens_list)-1:
                self.posting_lists[num_of_pl].append((self.tokens_list[i][1], count_tokens))
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                break

            if self.tokens_list[i][0] == self.tokens_list[i+1][0]:
                if self.tokens_list[i][1] == self.tokens_list[i+1][1]:
                    count_tokens += 1
                else:
                    self.posting_lists[num_of_pl].append((self.tokens_list[i][1], count_tokens))
                    count_tokens = 1
            else:
                self.posting_lists[num_of_pl].append((self.tokens_list[i][1], count_tokens))
                if self.tokens_list[i][0][0] != self.tokens_list[i+1][0][0]:   #checking if need to create new buffer of posting lists for new letter
                    self.posting_lists.append([])
                    num_of_pl += 1
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                loc_string = len(self.string)
                loc_posting_list = len(self.posting_lists[num_of_pl])

    def write_index_to_files(self, dir):

        try:
            os.mkdir(dir)
        except OSError as error:
            pass

        with open(f"{dir}//string_file.txt","w") as str_file:
            str_file.write(self.string)
        with open(f"{dir}//dict_file.bin","bw") as dict_file:
            dict_buff = bytes(0)
            for term in self.dictionary:
                dict_buff += struct.pack("ii", *term)
            dict_file.write(dict_buff)

        for i in range(len(self.posting_lists)):
            with open (f"{dir}//pl_{i}.bin","bw") as pl_file:
                pl_buff = bytes(0)
                for post in self.posting_lists[i]:
                    pl_buff += struct.pack("ii", *post)
                pl_file.write(pl_buff)

        with open(f"{dir}//reviews.bin", "bw") as reviews_file:
            reviews_file.write(self.reviews_buf)


    def print_dictionary(self):
        for i in range(len(self.dictionary)-1):
            print(f"{self.string[self.dictionary[i][0]:self.dictionary[i+1][0]]} \t {self.dictionary[i][1]}")
        print(f"{self.string[self.dictionary[i+1][0]:]} \t {self.dictionary[i+1][1]}")
        print(f"num of tokens {len(self.dictionary)}")

    def normalize(self, text):
        text = text.lower()
        text = re.split('\W+', text)
        return text


    def binary_search(self,  word, left):
        right = len(self.dictionary)
        while left < right:
            mid = (left+right-1)//2
            loc = self.dictionary[mid][0]
            if mid + 1 == len(self.dictionary):
                next_loc = -1
            else:
                next_loc = self.dictionary[mid+1][0]
            if self.string[loc:next_loc] == word:
                return True, mid
            elif self.string[loc:next_loc] < word: # string appears before word
                left = mid+1
            else:
                right = mid-1
        return False, right

    def removeIndex(self,dir):
        shutil.rmtree(dir, ignore_errors=True)





S = SlowIndexWriter("reviews//Books100.txt", "dir")
