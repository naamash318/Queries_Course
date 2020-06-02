import MiniIndexWriter
import struct

class IndexWriter:
    maxBytes = 100*(2**20)

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
                state = 0
                for i in range(0, count, 2):
                    with open(f"{dir}//l{state}//dir{i}//dict_file.bin") as dictionary1:
                        dict1 = dictionary1.read()
                    with open(f"{dir}//l{state}//dir{i+1}//dict_file.bin") as dictionary2:
                        dict2 = dictionary2.read()
                    with open(f"{dir}//l{state}//dir{i}//string_file.txt") as string_file1:
                        string1 = string_file1.read()
                    with open(f"{dir}//l{state}//dir{i+1}//string_file.txt") as string_file2:
                        string2 = string_file2.read()
                    self.mergeIndex(dict1, dict2, string1, string2)
                count = count//2
                state += 1
                if count < 1:
                    break;

    def mergeIndex(self, dict1, dict2, string1, string):
        string = ''
        word_loc1 = struct.unpack("i", dict1[0:4])[0]
        word_loc1_next = struct.unpack("i", dict1[8:12])[0]
        word_loc2 = struct.unpack("i", dict2[0:4])[0]
        word_loc2_next = struct.unpack("i", dict2[8:12])[0]
        word1 = string1[word_loc1: word_loc1_next]
        word2 = string1[word_loc2:word_loc2_next]
        if word1 < word2:
            string += word1
        elif word2 < word1:
            string += word2
        else




    """Delete all index files by removing the given directory"""
    def removeIndex(self, dir):