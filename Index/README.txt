======================================
Dassi Krakinovski, Naama Swimmer
ID:318525920, 318754066
=======================================

EX1 - Index structure

==Submitted Files==
README.txt - This file.
SlowIndexWriter.py - The create index code. This code create the index and the posting lists.
IndexReader.py - The query code. This code runs queries on existing index.

==How to compile and run==
python SlowIndexWriter.py
python IndexReader.py

===Comments:===
-- The IndexReader.py file reads from the index only after the index has been built and has not changed since its built.
-- The amount of words in the collection does not exceed 2^32 words.
-- The index consists of all the reviews including all fields and not just the text.
-- The user inserts a token consisting of one word (alphanumeric word).
