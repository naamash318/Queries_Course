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
    Creates an Index on the disk.
    
    Input:  inputFile:  The path to the file containing the review data
            dir:        The directory in which all index files will be created, if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""
    def __init__(self, inputFile, dir):

        with open(inputFile) as text_file:
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
        self.crete_empty_pl()
        self.create_index()
        #self.print_dictionary()
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
            #Sprint("successfully added review to buf ")
            return 0

        except ValueError as error:
            print("error with review's values")
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
        loc_string=0
        loc_posting_list = 0

        for i in range(len(self.tokens_list)):
            ch = self.convert_char_int(self.tokens_list[i][0][0])
            if i == len(self.tokens_list)-1:
                self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                break

            if self.tokens_list[i][0] == self.tokens_list[i+1][0]:
                if self.tokens_list[i][1] == self.tokens_list[i+1][1]:
                    count_tokens += 1
                else:
                    self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                    count_tokens = 1
            else:
                self.posting_lists[ch].append((self.tokens_list[i][1], count_tokens))
                self.string += self.tokens_list[i][0]
                self.dictionary.append((loc_string, loc_posting_list))
                if i != 0 and self.tokens_list[i][0][0] != self.tokens_list[i+1][0][0]:
                    loc_posting_list = 0
                else:
                    loc_posting_list = len(self.posting_lists[ch])
                loc_string = len(self.string)
                count_tokens = 1
        self.dictionary.append(len((self.tokens_list)))

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
        with open(f"{dir}//string_file.txt","w") as str_file:
            str_file.write(self.string)

        # write dictionary
        with open(f"{dir}//dict_file.bin","bw") as dict_file:
            dict_buff = bytes(0)
            for i in range(0, len(self.dictionary)-1):
                dict_buff += struct.pack("ii", *self.dictionary[i])
            dict_buff += struct.pack("i", self.dictionary[i+1])
            dict_file.write(dict_buff)

        # write 36 files of posting lists
        for i in range(len(self.posting_lists)):
            with open (f"{dir}//pl_{i}.bin","bw") as pl_file:
                pl_buff = bytes(0)
                for post in self.posting_lists[i]:
                    pl_buff += struct.pack("ii", *post)
                pl_file.write(pl_buff)

        # write reviews file
        with open(f"{dir}//reviews.bin", "bw") as reviews_file:
            reviews_file.write(self.reviews_buf)

    """ Help function, prints the dictionary"""
    def print_dictionary(self):
        for i in range(len(self.dictionary)-2):
            print(f"{self.string[self.dictionary[i][0]:self.dictionary[i+1][0]]} \t {self.dictionary[i][1]}")
        print(f"{self.string[self.dictionary[i+1][0]:]} \t {self.dictionary[i+1][1]}")
        print(f"num of tokens {len(self.dictionary)}")

    """-----------------------------------------------------------------------------------------------------------------
    Normalizing a text.
    
    input: text: string
    output: a list of tokens in the text
    -----------------------------------------------------------------------------------------------------------------"""
    def normalize(self, text):
        text = text.lower()
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
            return ord(char)-48
        if char >= 'a':
            return ord(char) - 87

    """-----------------------------------------------------------------------------------------------------------------
    Removing the entire Index from the disk
    Input: dir of index
    -----------------------------------------------------------------------------------------------------------------"""
    def removeIndex(self,dir):
        shutil.rmtree(dir, ignore_errors=True)


