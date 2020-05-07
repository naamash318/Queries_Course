import re
import os
import struct
import binascii
import json

def reverseList(aList):
    rev = aList[::-1]
    return rev


class SlowIndexWriter:
    reviews_counter = 0
    reviews_buf = bytes(4)
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
            self.add_to_index(text[start_review:end_review])
            start_review=end_review

        reviews_file = open("reviews.bin", "bw")
        reviews_file.write(self.reviews_buf)
        reviews_file.close()

        # reviews = text.split("product/productId: ")
        # for review in reviews:
        #     self.add_review(review)
        #     # add_to_index(review)



        # normal_text = self.normalize(text)
        # normal_text.sort()
        # self.reviews_counter+=1
        # print(normal_text)

        # review_id = 1 #need to be remove!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # try:
        #     os.mkdir("index")
        # except OSError as error:
        #     pass
        #
        # count = 1
        # for i in range(1, len(normal_text),count):
        #     word = normal_text[i]
        #     if i<len(normal_text) and word == normal_text[i+1]:
        #         count += 1
        #         continue
        #     self.insertToFile(word[0], word, review_id, count)
        #     count = 1
        #
        #     # count=1
        #     # word = normal_text[i]
        #     # print(i)
        #     # while word == normal_text[i+1]:
        #     #     count+=1
        #     #     i+=1
        #     # self.insertToFile(word[0], word, review_id , count)


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
            review_len = len(review)

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
    def add_to_index(self, review):
        review_tokens = self.normalize(review)
        num_of_tokens =len(review_tokens)
        print(review_tokens)

        pre_dict_list= []
        curr_list =[]
        count = 1
        ch = 97  # 'a' ascii code
        for i in range(1,num_of_tokens):
            word = review_tokens[i]
            if ord(word[0]) >= ch:
                pre_dict_list.append(curr_list)
                curr_list=[]
                while ord(word[0]) >= ch:
                    ch += 1
            if i+1 == num_of_tokens or word != review_tokens[i+1]:
                curr_list.append((word,count))
                count = 1
            else:
                count += 1

        pre_dict_list.append(curr_list)
        print(pre_dict_list)
        self.insert_to_index(pre_dict_list)

    """ התחלתי לעבוד על זה ודיי נתקעתי..."""
    def insert_to_index(self,tokens_list):
        # first review
        if self.reviews_counter == 1:
            for tl in tokens_list:
                posting_list_buffer =



   # def add_word_to_dictionary(self, word, review_id, count):





    def normalize(self, text):
        text = text.lower()
        text = re.split('\W+', text)
        text.sort()
        return text
    #
    # def removeIndex(self, dir): """Delete all index files by removing the given directory"""
    # def insertToFile(self, file_name, word, review_id, count):
    #     string_file = open(f"index//{file_name}.txt", 'r+')
    #     data_file = open(f"index//{file_name}.csv", 'r+')
    #
    #
    #     string = string_file.read()
    #     data = data_file.read()
    #     if data=='':
    #         string = word
    #         data = f"0,{count},{review_id}"
    #         string_file.seek(0)
    #         data_file.seek(0)
    #         string_file.write(string)
    #         data_file.write(data)
    #         string_file.close()
    #         data_file.close()
    #         return
    #     data = data.split('\n')
    #     exist, loc = self.binary_search(data, string, word)
    #     if exist:
    #         line = data[loc].split(',')
    #         line[1] = int(line[1]) + count
    #         line[2] = line[2] + " " + review_id
    #         data[loc] = line[0] + "," + line[1] + "," + line[2]
    #     else:
    #         pointer = data[loc].split(',')[0]
    #         line = f"{pointer},{count},{review_id}\n"
    #         data.insert(loc, line)
    #         updated_data = self.update_data(data, loc, len(word))
    #         string = string[:pointer] + word + string[pointer:]
    #         string_file.write(string)
    #
    #     data_file.write("".join(data))
    #     string_file.close()
    #     data_file.close()
    #
    # def update_data(self, data, loc, w_len):
    #     for i in range(loc+1, len(data)):
    #         line = data[i].split(',')
    #         line[0] = int(line[0]) + w_len
    #         data[i] = line[0] + "," + line[1] + "," + line[2]
    #     return data
    #
    # def binary_search(self, data, string, word):
    #     left = 0
    #     right = len(data)
    #     while left <= right:
    #         mid = (left+right-1)//2
    #         loc = int(data[mid].split(',')[0])
    #         next_loc = int(data[mid+1].split(',')[0])
    #         if string[loc:next_loc] == word:
    #             return True, mid
    #         elif string[loc:next_loc] < word: # string appears before word
    #             left = mid+1
    #         else:
    #             right = mid-1
    #     return False, right
    #
    #




S = SlowIndexWriter("reviews//review1.txt", "dir")