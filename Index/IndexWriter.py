import MiniIndexWriter
import struct

class IndexWriter:
    maxBytes = 100*(2**20)
    posting_list = []
    mini_pl = b''
    state = 0
    path1 = ""
    path2 = ""

    """Given product review data, creates an on disk index inputFile is the path to the file containing the review data dir is the directory in which all index files will be created
     if the directory does not exist, it should be created"""
    def write(self, inputFile, dir):
        with open(inputFile) as text_file:
            count = 0
            while True:
                text = text_file.read(self.maxBytes)
                if text == '':
                    break
                count += 1
                index = MiniIndexWriter.MiniIndexWriter(text, f"{dir}//l0//dir{count}")
            while True:
                self.state = 0
                for i in range(0, count, 2):
                    self.path1 = f"{dir}//l{self.state}//dir{i}"
                    self.path2 = f"{dir}//l{self.state}//dir{i+1}"
                    with open(f"{self.path1}//dict_file.bin") as dictionary1:
                        dict1 = dictionary1.read()
                    with open(f"{self.path2}/dict_file.bin") as dictionary2:
                        dict2 = dictionary2.read()
                    with open(f"{self.path1}//string_file.txt") as string_file1:
                        string1 = string_file1.read()
                    with open(f"{self.path2}//string_file.txt") as string_file2:
                        string2 = string_file2.read()
                    self.mergeIndex(dict1, dict2, string1, string2)
                count = count//2
                self.state += 1
                if count < 1:
                    break;

    def mergeIndex(self, dict1, dict2, string1, string2):
        string = ''
        flag = 0
        i = 0
        j =0
        letter = ""
        while flag == 0:
            word_loc1 = struct.unpack("i", dict1[i:i+4])[0]
            word_loc1_next = struct.unpack("i", dict1[i+8:i+12])[0]
            word_loc2 = struct.unpack("i", dict2[j:j+4])[0]
            word_loc2_next = struct.unpack("i", dict2[j+8:j+12])[0]
            word1 = string1[word_loc1: word_loc1_next]
            word2 = string2[word_loc2: word_loc2_next]
            if word1 < word2:
                string += word1
                i += 8
                self.mragePl(word1, letter, 1)
                letter = word1 [0]
            elif word2 < word1:
                letter = word2 [0]
                string += word2
            else

            if word_loc1_next == "":
                flag = 1
            if word_loc2_next == "":
                flag = 2


    def mragePl(self, word, pl, word_num):
        letter = word [0]
        if word [0] != pl:
            self.write_pl(pl)
            self.posting_list.clear()
            if word [0] >= 'a':
                letter = ord(word [0]) - 87
            if word_num == 1:
                with open(f"{self.path1}//pl_{letter}.bin") as posting_l:
                    mini_pl = posting_l.read()
        self.posting_list.append()

    def write_pl(pl):

    def term_info(self,dict):

    """Delete all index files by removing the given directory"""
    def removeIndex(self, dir):