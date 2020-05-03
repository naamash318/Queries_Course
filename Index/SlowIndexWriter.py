import re
import os
import json


class SlowIndexWriter:
    reviews_counter = 0

    """------------------------------------------------------------------------------------------------------
    Given product review data, creates an on disk index
    inputFile is the path to the file containing the review data
    dir is the directory in which all index files will be created
    if the directory does not exist, it should be created
    ---------------------------------------------------------------------------------------------------------"""
    def __init__(self, inputFile, dir):

        temp_file = open("temp.txt", 'a+')
        print(temp_file)
        text_file = open(inputFile)
        text = text_file.read()
        normal_text = self.normalize(text)
        normal_text.sort()
        self.reviews_counter+=1
        print(normal_text)

        review_id = 1 #need to be remove!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        try:
            os.mkdir("index")
        except OSError as error:
            pass

        count = 1
        for i in range(1, len(normal_text),count):
            word = normal_text[i]
            if i<len(normal_text) and word == normal_text[i+1]:
                count += 1
                continue
            self.insertToFile(word[0], word, review_id, count)
            count = 1

            # count=1
            # word = normal_text[i]
            # print(i)
            # while word == normal_text[i+1]:
            #     count+=1
            #     i+=1
            # self.insertToFile(word[0], word, review_id , count)




    def removeIndex(self, dir): """Delete all index files by removing the given directory"""

    def normalize(self, text):
        text = text.lower()
        text = re.split('\W+', text)
        return text

    def insertToFile(self, file_name, word, review_id, count):
        string_file = open(f"index//{file_name}.txt", 'r+')
        data_file = open(f"index//{file_name}.csv", 'r+')


        string = string_file.read()
        data = data_file.read()
        if data=='':
            string = word
            data = f"0,{count},{review_id}"
            string_file.seek(0)
            data_file.seek(0)
            string_file.write(string)
            data_file.write(data)
            string_file.close()
            data_file.close()
            return
        data = data.split('\n')
        exist, loc = self.binary_search(data, string, word)
        if exist:
            line = data[loc].split(',')
            line[1] = int(line[1]) + count
            line[2] = line[2] + " " + review_id
            data[loc] = line[0] + "," + line[1] + "," + line[2]
        else:
            pointer = data[loc].split(',')[0]
            line = f"{pointer},{count},{review_id}\n"
            data.insert(loc, line)
            updated_data = self.update_data(data, loc, len(word))
            string = string[:pointer] + word + string[pointer:]
            string_file.write(string)

        data_file.write("".join(data))
        string_file.close()
        data_file.close()

    def update_data(self, data, loc, w_len):
        for i in range(loc+1, len(data)):
            line = data[i].split(',')
            line[0] = int(line[0]) + w_len
            data[i] = line[0] + "," + line[1] + "," + line[2]
        return data

    def binary_search(self, data, string, word):
        left = 0
        right = len(data)
        while left <= right:
            mid = (left+right-1)//2
            loc = int(data[mid].split(',')[0])
            next_loc = int(data[mid+1].split(',')[0])
            if string[loc:next_loc] == word:
                return True, mid
            elif string[loc:next_loc] < word: # string appears before word
                left = mid+1
            else:
                right = mid-1
        return False, right






S = SlowIndexWriter("reviews//review1.txt", "dir")