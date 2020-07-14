"""---------------------------------------------------------------------------------------------------------------------
Dassi Krakinovski:  318525920
Naama Swimmer:      318754066
---------------------------------------------------------------------------------------------------------------------"""

import glob
from math import log
import MiniIndexWriter
import struct
import os
import shutil
import compress
from datetime import datetime

size_of_dic_value = 8   # 2 integers

"""---------------------------------------------------------------------------------------------------------------------
Public Functions
---------------------------------------------------------------------------------------------------------------------"""

def to_char(char):
    if char <= '9':
        return ord(char) - 48
    if char >= 'a':
        return ord(char) - 87

def remove_state(dir, state):
    dir_list = glob.glob(f"{dir}_l{state}*")
    print(dir_list)
    for d in dir_list:
        shutil.rmtree(d, ignore_errors=True)


"""---------------------------------------------------------------------------------------------------------------------
Index Class:

This class display an index and used while merging. 
It holds the dictionary and includes method to run over the posting lists.

Properties:
    - path = the index directory
    - dictionary = the dict file
    - string = the terms as a long string
    - curr_letter = the current term's first letter
    - curr_pointer = pointer to the current term in the dict file
    - next_pointer = pointer to the next term in the dict file
    - curr_pl_file = a file descriptor to the current letter posting list file
    
Functions:
    - get_curr_word_and_pl = 
    The function goes over the dictionary and each time it will return the current word an its posting list.
    
---------------------------------------------------------------------------------------------------------------------"""


class Index:

    curr_letter = '-1'
    curr_pointer = 0
    next_pointer = size_of_dic_value
    curr_pl_file = None

    def __init__(self, path):
        self.path = path
        with open(f"{path}//dict_file.bin", "br") as dict_file:
            self.dictionary = dict_file.read()
        with open(f"{path}//string_file.txt") as string_file:
            self.string = string_file.read()

    def get_curr_word_and_pl(self):

        if self.curr_pointer == len(self.dictionary):
            return -1
        word_loc,pl_offset = struct.unpack("ii", self.dictionary[self.curr_pointer:self.curr_pointer + size_of_dic_value])
        if self.next_pointer < len(self.dictionary):
            next_word_loc, next_pl_offset = struct.unpack("ii", self.dictionary[self.next_pointer:self.next_pointer + size_of_dic_value])
            curr_word = self.string[word_loc:next_word_loc]
            length = next_pl_offset - pl_offset
        else:   #last term
            curr_word = self.string[word_loc:]
            length = -1

        if curr_word[0] != self.curr_letter:
            if self.curr_pl_file != None:
                self.curr_pl_file.close()
            self.curr_letter = curr_word[0]
            self.curr_pl_file = open(f"{self.path}//pl_{to_char(self.curr_letter)}.bin", "br")
        if length <= 0:
            curr_pl = self.curr_pl_file.read()   #read till end of file
        else:
            curr_pl = self.curr_pl_file.read(length)

        self.curr_pointer = self.next_pointer
        self.next_pointer += size_of_dic_value

        return curr_word, curr_pl


"""---------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------
The Main class : IndexWriter
------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------"""

class IndexWriter:

    maxBytes = 150*(2**20)  #150 MB
    #maxBytes = 1000*(2**10)
    posting_list = []
    main = False

    """------------------------------------------------------------------------------------------------------
    Creates an Index on the disk.

    Input:  inputFile:  The path to the file containing the review data
            dir:        The directory in which all index files will be created, if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""
    def __init__(self, inputFile, dir):

        indexes_count, reviews_count, tokens_count = self.build_mini_indexes(inputFile, dir)
        if indexes_count > 1:
            self.merge(dir, indexes_count)
        #shutil.move("reviews.bin", f"{dir}//reviews.bin")
        with open(f"{dir}//general.txt", 'w') as general_file:
            general_file.write(f"{reviews_count}\n{tokens_count}")

    """------------------------------------------------------------------------------------------------------
        Build mini Indexes.

        For each index reading 150 Mb.
        ---------------------------------------------------------------------------------------------------------"""

    def build_mini_indexes(self, inputFile, dir):
        reviews_count = 0
        tokens_count = 0
        text = ""
        file_size = os.stat(inputFile).st_size

        with open(inputFile) as text_file:
            count = 0
            if file_size < self.maxBytes:
                text = text_file.read()
                index = MiniIndexWriter.MiniIndexWriter(text, f"{dir}", reviews_count)
                tokens_count = index.num_tokens
                reviews_count = index.reviews_counter
                return 1, reviews_count, tokens_count

            while True:
                text += text_file.read(self.maxBytes)
                if text == '':
                    break

                end = None
                left = ""
                if text_file.tell() != file_size:    # the last review might not completely read so will be send in the next time
                    end = text.rfind("product/productId: ")
                    left = text[end:]
                print(f"start building mini index {count}: {datetime.now().strftime('%H:%M:%S')}")
                index = MiniIndexWriter.MiniIndexWriter(text[:end], f"{dir}_l0_dir{count}", reviews_count)
                print(f"finished building mini index {count}: {datetime.now().strftime('%H:%M:%S')}")
                text = left
                reviews_count = index.reviews_counter
                tokens_count += index.num_tokens
                count += 1

        return count, reviews_count, tokens_count

    """------------------------------------------------------------------------------------------------------
        Merge the mini indexes into one index.
        ---------------------------------------------------------------------------------------------------------"""
    def merge(self, dir, count):
        # merging indexes
        state = 0
        save = ""
        main = False

        while not main:

            for i in range(0, count, 2):

                path1 = f"{dir}_l{state}_dir{i}"
                path2 = f"{dir}_l{state}_dir{i+1}"
                path = f"{dir}_l{state + 1}_dir{(i + 1) // 2}"
                if i == count - 1:
                    if save != "":
                        path2 = save
                        save = ""
                        count += 1

                    else:
                        save = path1
                        break

                if count <= 2 and save == "":
                    path = dir
                    main = True
                    print("the main one")

                print(f"state {state} merging indexes {i} , {i + 1} path1: {path1} path2:{path2} merged: {path}")
                print(f"start merging: {datetime.now().strftime('%H:%M:%S')}")
                self.mergeIndex(path, path1, path2, main)
                print(f"finish merging: {datetime.now().strftime('%H:%M:%S')}")
                shutil.rmtree(path1, ignore_errors=True)
                shutil.rmtree(path2, ignore_errors=True)

            count = count // 2
            state += 1

    """------------------------------------------------------------------------------------------------------
        Getting 2 pathes to indexes and merging them
    ---------------------------------------------------------------------------------------------------------"""
    def mergeIndex(self, path, path1, path2, main):

        string = ''
        index1 = Index(path1)
        index2 = Index(path2)
        letter = '0'
        dic = []
        term1 = index1.get_curr_word_and_pl()
        term2 = index2.get_curr_word_and_pl()

        try:
            os.mkdir(path)
        except OSError as error:
            pass

        pl_file = open(f"{path}//pl_{to_char(letter)}.bin", "bw")

        while term1 != -1 or term2 != -1:

            if term1 == -1:
                add_term = term2
                term2 = index2.get_curr_word_and_pl()
            elif term2 == -1:
                add_term = term1
                term1 = index1.get_curr_word_and_pl()
            elif term1[0] == term2[0]:
                #print(f"term : {term1[0]}")
                merged_pl = self.merge_pl(term1[1], term2[1])
                add_term = (term1[0],merged_pl)
                term1 = index1.get_curr_word_and_pl()
                term2 = index2.get_curr_word_and_pl()
            elif term1[0] < term2[0]:
                add_term = term1
                term1 = index1.get_curr_word_and_pl()
            else:   # term1[0] > term2[0]:
                add_term = term2
                term2 = index2.get_curr_word_and_pl()

            if add_term[0][0] != letter:
                pl_file.close()
                letter = add_term[0][0]
                pl_file = open(f"{path}//pl_{to_char(letter)}.bin", "bw")

            dic.append((len(string), pl_file.tell()))
            string += add_term[0]
            pl_file.write(add_term[1])

        self.write_to_file(path,dic,string)


    def write_to_file(self,path,dic,string):
        dict_buff = bytes(0)
        for i in range(0, len(dic)):
            dict_buff += struct.pack("ii", *dic[i])
        with open(f"{path}//dict_file.bin", "bw") as dict_file:
            dict_file.write(dict_buff)

        with open(f"{path}//string_file.txt", "w") as str_file:
            str_file.write(string)


    def merge_pl(self,pl1,pl2):
        pl_buff = b''
        un_pl1 = compress.uncompress_pl(pl1)
        un_pl2 = compress.uncompress_pl(pl2)

        #find last review id for update diffs
        review_num = 0
        for i in range(0,len(un_pl1), 2):
            review_num += un_pl1[i]
        temp = un_pl2[0]
        un_pl2[0] = un_pl2[0] - review_num

        merged = compress.compress_pl(un_pl1 + un_pl2, un_pl1, un_pl2)
        pl_buff += pl1 + bytes(2) + pl2
        return merged



    """Delete all index files by removing the given directory"""
    def removeIndex(self, dir):
        shutil.rmtree(dir, ignore_errors=True)


# start = datetime.now()
# start_time = start.strftime("%H:%M:%S")
#
# s = IndexWriter("reviews\\Books100.txt", "my_dir")
# end = datetime.now()
# end_time = end.strftime("%H:%M:%S")
# print("Start Time =", start_time)
# print("End Time =", end_time)

