import IndexReader
import IndexWriter
import string
import random
import argparse
import sys


sp = ["1special1","2special2","3SPECIAL3","4special4","5Special5"]
rv = [[],[],[],[],[]]
a1 = []
a2 = []
a3 = []


def test(num, count):

    errors = 0
    print("Building index")
    IndexWriter.IndexWriter("test_file.txt", "test_dir")
    print("build done")

    print("building reader")
    index = IndexReader.IndexReader("test_dir")
    print("reader done")

    print("=============================================================================================================")
    print(" checking function getTokenFrequency ")

    for i in range(len(sp)):
        t = index.getTokenFrequency(sp[i])
        if t != a2[i]:
            print(f"Error function getTokenFrequency return {t} for term {sp[i]} instead of {a2[i]}")
            errors += 1
    print("Finish testing getTokenFrequency function ")


    print("=============================================================================================================")
    print(" checking function getTokenCollectionFrequency ")

    for i in range(len(sp)):
        t = index.getTokenCollectionFrequency(sp[i])
        if t != a1[i]:
            print(f"Error function getTokenCollectionFrequency return {t} for term {sp[i]} instead of {a1[i]}")
            errors += 1

    print("Finish testing getTokenCollectionFrequency function ")


    print("=============================================================================================================")
    print(" checking function getReviewsWithToken ")

    for i in range(len(sp)):
        t = index.getReviewsWithToken(sp[i])
        if t != a3[i]:
            print(f"Error function getReviewsWithToken return {t} for term {sp[i]} instead of {a3[i]}")
            errors += 1

    print("Finish testing getReviewsWithToken function ")


    print("=============================================================================================================")
    print(" checking function getTokenSizeOfReviews ")

    s= index.getTokenSizeOfReviews()
    if s!= count:
        print(f"Error function getTokenSizeOfReviews return {s} ")
        errors+=1
    print("Finish testing getTokenSizeOfReviews function ")

    print("=============================================================================================================")
    print(" checking function getNumberOfReviews ")

    s = index.getNumberOfReviews()
    if s!= num:
        print(f"Error function getNumberOfReviews return {s} ")
        errors+=1
    print("Finish testing getNumberOfReviews function ")

    print("\n\n-------------------------------------------------------------------------------------------------------------")
    print(f"\nFinished testing with {errors} errors")




def prepar_answers():

    for l in rv:
        a1.append(len(l))
        ll = list(dict.fromkeys(l))
        a2.append(len(ll))
        my_dict = {i: l.count(i) for i in l}
        li =[]
        for k,v in my_dict.items():
            li.append(k)
            li.append(v)
        a3.append(tuple(li))



def get_random_string(length):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    #print("Random string of length", length, "is:", result_str)
    return result_str


def create_text(rev_num):
    count =0
    length = random.randint(10,200)
    str = "";
    for i in range(length):
        str+=" "+get_random_string(random.randint(2,8))
        count += 1
        stam = random.randint(0,1000)
        if stam < 5:
            str +=" "+sp[stam]
            rv[stam].append(rev_num)
            count += 1

    return count,str

def create_inputfile(num):
    general_str = "product/productId: B000NKGYMK\nproduct/title: Alaska Sourdough\nproduct/price: unknown\nreview/userId: AC58Z72OB2DDX\nreview/profileName: Gary W. Marian\nreview/helpfulness: 29/30\nreview/score: 5.0\nreview/time: 945734400\nreview/summary: True Alaskan cooking\nreview/text: "
    global_count = 0
    with open("test_file.txt","w") as f:
        for i in range(0,num):
            c,text = create_text(i+1)
            f.write(general_str + text + "\n\n")
            global_count += c
    return global_count



def parse_args(args):

    usage_string = "Test.py -r <number of revies>"
    parser = argparse.ArgumentParser(usage=usage_string, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', action = 'store', required = False,  help='number of reviews')
    parser.add_argument('-p', action='store', required=False, help='path to inputfile')
    args = parser.parse_args(args)

    return args

if __name__ == "__main__":
    try:
        args = parse_args(sys.argv[1:])
        if args.r!=None:
            c = create_inputfile(int(args.r))
            prepar_answers()
            test(int(args.r),c)
        if args.p!= None:
            print("Building Index")
            IndexWriter.IndexWriter(args.p, "dir")

        print("\n\nfinished")
    except Exception as e:
        print(e)
        sys.exit(3)