"""---------------------------------------------------------------------------------------------------------------------
Dassi Krakinovski:  318525920
Naama Swimmer:      318754066
---------------------------------------------------------------------------------------------------------------------"""
import re
import os
import struct
import shutil
from math import log


class MiniIndexWriter:
    reviews_counter = 0
    reviews_buf = bytes(0)
    tokens_list = []
    posting_lists = []
    dictionary = []
    string = ""

    """------------------------------------------------------------------------------------------------------
    Creates an Index on the disk.

    Input:  inputFile:  The path to the file containing the review data
            dir:        The directory in which all index files will be created, if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""

    def __init__(self, inputFile, dir):
        with open(inputFile) as text_file:
            text = text_file.read()
        #text = inputFile
        start_review = text.find("product/productId: ")
        while start_review != -1:
            end_review = text.find("product/productId: ", start_review + 1)
            start_text = text.find("review/text: ", start_review + 1)
            if self.add_review(text[start_review:start_text], text[start_text + 13:end_review]) != 0:
                start_review = end_review
                continue
            self.reviews_counter += 1
            self.add_to_list(text[start_text + 13:end_review])
            start_review = end_review

        self.tokens_list.sort()
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

    def add_review(self, review, text):
        val = ["product/productId: ", "review/helpfulness: ", "review/score: "]
        try:
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
            review_score = chr(int(float(review[loc:end_line])))  # 1 byte cnverted from string to float to int t char

            # calculate review len (number of tokens)
            text = re.split(r'[_\b\W]+', text)
            text = list(filter(None, text))
            review_len = len(text)
            # pack review data into binary struct
            review_tuple = (
            product_id.encode('ascii'), review_score.encode(), helpfulness_numerator, helpfulness_denominator,
            review_len)
            review_format = "10s 1s i i  i"
            s = struct.Struct(review_format)
            packed_data = s.pack(*review_tuple)

            # print("packed review:")
            # print(binascii.hexlify(packed_data))
            # print("size of packed review:")
            # print(s.size)

            self.reviews_buf += packed_data
            # Sprint("successfully added review to buf ")
            return 0

        except ValueError as error:
            # print("error with review's values")
            return -1

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
                if i != 0 and self.tokens_list[i][0][0] != self.tokens_list[i + 1][0][0]:
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

        # write dictionary
        with open(f"{dir}//dict_file.bin", "bw") as dict_file:
            dict_buff = bytes(0)
            for i in range(0, len(self.dictionary)):
                dict_buff += struct.pack("ii", *self.dictionary[i])
            dict_file.write(dict_buff)

        # write 36 files of posting lists
        for i in range(len(self.posting_lists)):
            self.compress_pl(i)
            with open(f"{dir}//pl_{i}.bin", "bw") as pl_file:
                pl_buff = bytes(0)
                for post in self.posting_lists[i]:
                    pl_buff += struct.pack("ii", *post)
                pl_file.write(pl_buff)

        # write reviews file
        with open(f"{dir}//reviews.bin", "bw") as reviews_file:
            reviews_file.write(self.reviews_buf)


    def compress_pl(self, num_pl):
        num_bytes = [0,0,0,0]
        bytes_def = ["00", "01", "10", "11"]
        pl_buff = ""
        first_byte = '0'
        num_pl = 10
        print(self.posting_lists[num_pl])
        print(self.dictionary)
        print(self.string)
        print(self.string.find('a'))
        for i in range(len(self.posting_lists[num_pl])-1):
            self.posting_lists[num_pl][i] = ((self.posting_lists[num_pl][i+1][0] - self.posting_lists[num_pl][i][0], self.posting_lists[num_pl][i][1]))

        for i in range(0, len(self.posting_lists[num_pl])-1, 2):
            num_bytes[0] = self.bytes_needed(self.posting_lists[num_pl][i][0])
            print(self.posting_lists[num_pl][i][0])
            print(self.bytes_needed(self.posting_lists[num_pl][i][0]))
            num_bytes[1] = self.bytes_needed(self.posting_lists[num_pl][i][1])
            num_bytes[2] = self.bytes_needed(self.posting_lists[num_pl][i+1][0])
            num_bytes[3] = self.bytes_needed(self.posting_lists[num_pl][i+1][1])
        print(num_bytes)
        first_byte |= num_bytes[0] >> 3
        first_byte |= num_bytes[1] >> 2
        first_byte |= num_bytes[2] >> 1
        first_byte |= num_bytes[3] >> 0

        #pl_buff += bytes_def[num_bytes[0]-1] + bytes_def[num_bytes[1]-1] + bytes_def[num_bytes[2]-1] + bytes_def[num_bytes[3]-1]


    def bytes_needed(self, num):
        # if num == 0:
        #     return 1
        # return int(log(num, 256)) + 1
        return (num.bit_length() + 7) // 8


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

    def get_word_and_postList(id):
        # get the word
        word_loc = self.dictionary[id][0]
        next_word_loc = self.dictionary[id+1][0]
        word = self.string[word_loc: next_word_loc]

        # get the post List
        pl_pointer = self.dictionary[id][1]
        next_pl_pointer = self.dictionary[id+1][1]
        letter = convert_char_int(word[0])

        if next_pl_pointer > pl_pointer:
            pl = self.posting_lists[letter][pl_pointer:next_pl_pointer]
        else:   # the last post list on the file
            pl = self.posting_lists[letter][pl_pointer:]

        return word, pl

    def compress_and_write(self):
        ch =0
        pl_file = open(f"{dir}//pl_{ch}.bin", "bw")
        for i in range(len(self.dictionary)):
            word, pl = self.get_word_and_postList(i)
            compressed_pl = self.compress_pl(pl)

            curr_ch = self.convert_char_int(word[0])
            if curr_ch != ch:
                pl_file.close()
                ch = curr_ch
                pl_file = open(f"{dir}//pl_{ch}.bin", "bw")

            pl_file.write(compressed_pl)

        pl_file.close()


    def compress_pl(self, pl):
        diff_pl = []
        curr_t_buff =b''
        pl_buff = b''

        diff_pl.append(pl[0])
        for i in range(len(pl)-1):
            diff = pl[i+1][0]-pl[i][0]
            diff_pl.append((diff, pl[i+1][1]))

        for i in range(0,len(pl),2):

            order = 0
            # if i+1 >= len(pl):
            #     curr_t = (pl_diff[i][0], pl_diff[i][1], 0, pl_diff[i + 1][1])
            curr_t = (diff_pl[i][0],diff_pl[i][1],diff_pl[i+1][0],diff_pl[i+1][1])

            for v in curr_t:
                bytes_need = bytes_needed(v)
                order >>= 2
                order |= bytes_need
                curr_t_buff += v.to_bytes(bytes_need, byteorder='little')

            pl_buff += order.to_bytes(1, byteorder='little')
            pl_buff += curr_t_buff

        return pl_buff


m = MiniIndexWriter("reviews//Books10.txt", "dir")
