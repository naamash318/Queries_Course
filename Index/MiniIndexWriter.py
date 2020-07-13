"""---------------------------------------------------------------------------------------------------------------------
Dassi Krakinovski:  318525920
Naama Swimmer:      318754066
---------------------------------------------------------------------------------------------------------------------"""
import re
import os
import struct
import shutil
import compress
import sys
from math import log


class MiniIndexWriter:

    reviews_buf = bytes(0)
    tokens_list = []
    posting_lists = []
    dictionary = []
    string = ""
    num_tokens = 0


    """------------------------------------------------------------------------------------------------------
    Creates an Index on the disk.

    Input:  inputFile:  The path to the file containing the review data
            dir:        The directory in which all index files will be created, if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""

    def __init__(self, text, dir, review_count):
        #text = inputFile
        start_review = text.find("product/productId: ")
        self.reviews_counter = review_count
        while start_review != -1:
            end_review = text.find("product/productId: ", start_review + 1)
            start_text = text.find("review/text: ", start_review + 1)
            if start_text == -1:
                start_review = end_review
                continue
            # if self.add_review(text[start_review:start_text], text[start_text + 13:end_review]) != 0:
            self.reviews_counter += 1
            self.add_to_list(text[start_text + 13:end_review])
            start_review = end_review
        del text
        self.tokens_list.sort()
        self.num_tokens += len(self.tokens_list)
        self.crete_empty_pl()
        self.create_index()
        # self.print_dictionary()
        self.write_index_to_files(dir)

    """-----------------------------------------------------------------------------------------------------------------
    Add a review values to the reviews buffer.

    Input:  review: A string which contains one review.
    Values to store:    -productId: 10 Bytes
                        -score: 1 Bytes
                        -helpfulness: 2 integers = 8 Bytes
                        -length: integer = 4 Bytes

    TODO: There is an empty byte between score to helpfulness due to struct alignments
    -----------------------------------------------------------------------------------------------------------------"""
    '''
    def add_review(self, review, text):
        val = ["product/productId: ", "review/helpfulness: ", "review/score: "]
        try:
            bin_buff = b''
            # Find product id
            loc = len(val[0])
            product_id = review[loc:loc + 10]

            # Find helpfulness
            loc = review.find(val[1]) + len(val[1])
            slash_loc = review.find("/", loc)
            end_line = review.find("\n", loc)
            helpfulness_numerator = int(review[loc:slash_loc])  # int = 3 bytes
            helpfulness_denominator = int(review[slash_loc + 1:end_line])  # int = 3 bytes

            # find score
            loc = review.find(val[2]) + len(val[2])
            end_line = review.find("\n", loc)
            review_score = int(float(review[loc:end_line]))  # 1 byte cnverted from string to float to int t char

            # calculate review len (number of tokens)
            text = re.split(r'[_\b\W]+', text)
            text = list(filter(None, text))
            review_len = len(text)
            # pack review data into binary struct
            bin_buff += product_id.encode('ascii')
            bin_buff += review_score.to_bytes(1, byteorder="little")
            bin_buff += helpfulness_numerator.to_bytes(4, byteorder="little")
            bin_buff += helpfulness_denominator.to_bytes(4, byteorder="little")
            bin_buff += review_len.to_bytes(2, byteorder="little")

            self.reviews_buf += bin_buff
            return 0

        except ValueError as error:
            # print("error with review's values")
            return -1
    '''
    """-----------------------------------------------------------------------------------------------------------------
    Adding the tokens of a review to the tokens list, for each tokens saving the reviewId
    Input: review: normalize review - a list of the tokens appear in the review 
    -----------------------------------------------------------------------------------------------------------------"""

    def add_to_list(self, review):

        review_tokens = self.normalize(review)
        for token in review_tokens:
            if token != '':
                self.tokens_list.append((token, self.reviews_counter))

    """-----------------------------------------------------------------------------------------------------------------
    Creating the dictionary and the posting lists.

    self.dictionary:    a list of tuples. 
                        each tuple contains: offset of word in the string, offset of the posting list.
                        The last variable in the list is the numbers of tokens in the collection. 
    self.posting lists: a list of lists, each list contains the posting list of tokens which start with one letter.
                        posting list is a list of tuples, each tuple contains: review_id, freq
    -----------------------------------------------------------------------------------------------------------------"""

    def create_index(self):
        count_tokens = 1
        loc_string = 0
        loc_posting_list = 0
        for i in range(len(self.tokens_list)):
            ch = self.convert_char_int(self.tokens_list[i][0][0])
            if i == len(self.tokens_list) - 1:
                self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                break

            if self.tokens_list[i][0] == self.tokens_list[i + 1][0]:
                if self.tokens_list[i][1] == self.tokens_list[i + 1][1]:
                    count_tokens += 1
                else:
                    self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                    count_tokens = 1
            else:
                self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                if self.tokens_list[i][0][0] != self.tokens_list[i + 1][0][0]:
                    loc_posting_list = 0
                else:
                    loc_posting_list = len(self.posting_lists[ch])
                loc_string = len(self.string)
                count_tokens = 1

    """-----------------------------------------------------------------------------------------------------------------
    Write the Index on the disk.

    Input: dir: The directory in which all index files will be created, if the directory does not exist, it should be created  
    -----------------------------------------------------------------------------------------------------------------"""

    def write_index_to_files(self, dir):

        # make directory
        try:
            os.mkdir(dir)
        except OSError as error:
            pass

        # write string
        with open(f"{dir}//string_file.txt", "w") as str_file:
            str_file.write(self.string)

        self.send_compress_pl(dir)
        # write dictionary
        with open(f"{dir}//dict_file.bin", "bw") as dict_file:
            dict_buff = bytes(0)
            for i in range(0, len(self.dictionary)):
                dict_buff += struct.pack("ii", *self.dictionary[i])
            dict_file.write(dict_buff)

        # write reviews file
        # with open("reviews.bin", "ba") as reviews_file:
        #     reviews_file.write(self.reviews_buf)


        # self.reviews_buf = bytes(0)
        self.tokens_list.clear()
        self.posting_lists.clear()
        self.dictionary.clear()
        self.string = ""

    '''-------------------------------------------------------------------------------------------------------------------------------------------------- 
    That's how I did it with copression : need to review it!!!
    -----------------------------------------------------------------------------------------------------------------------------------------------------'''
    def send_compress_pl(self, dir):
        buff_bytes = b''
        for i in range(len(self.dictionary)):
            loc = self.dictionary[i][1]
            pl = self.convert_char_int(self.string[self.dictionary[i][0]])
            if i + 1 == len(self.dictionary) or self.string[self.dictionary[i][0]] != self.string[self.dictionary[i + 1][0]]:
                next_loc = len(self.posting_lists[pl])
                self.dictionary[i] = (self.dictionary[i][0], len(buff_bytes))
                buff_bytes += self.compress_pl(pl, loc, next_loc)
                self.write_pl(buff_bytes, pl, dir)
                buff_bytes = b''
            else:
                next_loc = self.dictionary[i + 1][1]
                self.dictionary[i] = (self.dictionary[i][0], len(buff_bytes))
                buff_bytes += self.compress_pl(pl, loc, next_loc)



    def compress_pl(self, pl, loc, next_loc):

        pl_diffs = [self.posting_lists[pl][loc][0], self.posting_lists[pl][loc][1]]
        for i in range(loc, next_loc-1):
            diff = self.posting_lists[pl][i+1][0] - self.posting_lists[pl][i][0]
            pl_diffs.append(diff)
            pl_diffs.append(self.posting_lists[pl][i+1][1])
        return compress.compress_pl(pl_diffs, 0, 0)
    '''------------------------------------------------------------------------------------------------------------------------------------------------
    
    def send_compress_pl(self, dir):
        buff_bytes = b''
        for i in range(len(self.dictionary)):
            loc = self.dictionary[i][1]
            pl = self.convert_char_int(self.string[self.dictionary[i][0]])
            if i + 1 == len(self.dictionary) or self.string[self.dictionary[i][0]] != self.string[self.dictionary[i + 1][0]]:
                next_loc = len(self.posting_lists[pl])
                self.dictionary[i] = (self.dictionary[i][0], len(buff_bytes))
                buff_bytes += self.compress_pl(pl, loc, next_loc)
                self.write_pl(buff_bytes, pl, dir)
                buff_bytes = b''
            else:
                next_loc = self.dictionary[i + 1][1]
                self.dictionary[i] = (self.dictionary[i][0], len(buff_bytes))
                buff_bytes += self.compress_pl(pl, loc, next_loc)



    def compress_pl(self, pl, loc, next_loc):
        buff_bytes = b''
        for i in range(loc, next_loc-1):
            self.posting_lists[pl][i] = (self.posting_lists[pl][i+1][0] - self.posting_lists[pl][i][0], self.posting_lists[pl][i][1])
        for i in range(loc, next_loc, 2):
            if i == next_loc-1:
                first_byte, num_bytes = self.first_byte(i, pl, 2)
                buff_bytes += first_byte.to_bytes(1, byteorder='little')
                buff_bytes += self.bytes_pl(i, pl, num_bytes, 2)
            else:
                first_byte, num_bytes = self.first_byte(i, pl, 4)
                buff_bytes += first_byte.to_bytes(1, byteorder='little')
                buff_bytes += self.bytes_pl(i, pl, num_bytes, 4)
        return buff_bytes

    def first_byte(self, loc, pl, flag):
        num_bytes = [1, 1, 1, 1]
        first_byte = 0
        num_bytes[0] = (self.posting_lists[pl][loc][0].bit_length() + 7) // 8
        num_bytes[1] = (self.posting_lists[pl][loc][1].bit_length() + 7) // 8
        if flag != 2:
            num_bytes[2] = (self.posting_lists[pl][loc + 1][0].bit_length() + 7) // 8
            num_bytes[3] = (self.posting_lists[pl][loc + 1][1].bit_length() + 7) // 8
        for i in num_bytes:
            first_byte <<= 2
            first_byte |= i-1


        # print(f"first_byte is {first_byte}")
        # print(num_bytes)
        return first_byte, num_bytes

    def bytes_pl(self, loc, pl, num_bytes, flag):
        buf = b''
        buf += self.posting_lists[pl][loc][0].to_bytes(num_bytes[0], byteorder='little')
        buf += self.posting_lists[pl][loc][1].to_bytes(num_bytes[1], byteorder='little')
        if flag != 2:
            buf += self.posting_lists[pl][loc+1][0].to_bytes(num_bytes[2], byteorder='little')
            buf += self.posting_lists[pl][loc+1][1].to_bytes(num_bytes[3], byteorder='little')
        return buf
    '''
    def write_pl(self, buff, pl, dir):

        with open(f"{dir}//pl_{pl}.bin", "bw") as pl_file:
            pl_file.write(buff)

    """ Help function, prints the dictionary"""

    def print_dictionary(self):
        for i in range(len(self.dictionary) - 2):
            print(f"{self.string[self.dictionary[i][0]:self.dictionary[i + 1][0]]} \t {self.dictionary[i][1]}")
        print(f"{self.string[self.dictionary[i + 1][0]:]} \t {self.dictionary[i + 1][1]}")
        print(f"num of tokens {len(self.dictionary)}")

    """-----------------------------------------------------------------------------------------------------------------
    Normalizing a text.

    input: text: string
    output: a list of tokens in the text
    -----------------------------------------------------------------------------------------------------------------"""

    def normalize(self, text):
        text = text.lower()
        text = text.strip()
        text = re.split(r'[_\b\W]+', text)
        return text

    """-----------------------------------------------------------------------------------------------------------------
    Creating 36 empty list for posting lists
    -----------------------------------------------------------------------------------------------------------------"""

    def crete_empty_pl(self):
        for i in range(0, 36):
            self.posting_lists.append([])

    """-----------------------------------------------------------------------------------------------------------------
    Input: an alphanumeric character
    Output: The matching posting list file number
    -----------------------------------------------------------------------------------------------------------------"""

    def convert_char_int(self, char):
        if char <= '9':
            return ord(char) - 48
        if char >= 'a':
            return ord(char) - 87

    """-----------------------------------------------------------------------------------------------------------------
    Removing the entire Index from the disk
    Input: dir of index
    -----------------------------------------------------------------------------------------------------------------"""

    def removeIndex(self, dir):
        shutil.rmtree(dir, ignore_errors=True)
        self.reviews_counter = 0
        self.reviews_buf = bytes(0)
        self.tokens_list.clear()
        self.posting_lists.clear()
        self.dictionary.clear()
        self.string = ""

#m = MiniIndexWriter("reviews//Books1000.txt", "mini_dir_100", 0)
