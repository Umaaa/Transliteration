Transliteration
===============

To run the code for alignment:

1. If you don't have an answer file to compare with

python align.py  -n [iterations] -trainfile [path to train file]

Example:
python align.py  -n 5 -trainfile epron-jpron-unsupervised.data 

Two new files will be generated

a. epron-jpron.alignment
b. epron-jpron-unsupervised.wfst

2. If you have an answer file to compare with

python align.py  -n [iterations] -trainfile [path to train file] -checkfile [path to check file]

Example:
python align.py  -n 5 -trainfile epron-jpron-unsupervised.data -checkfile hw2/epron-jpron.data

Two new files will be generated

a. epron-jpron.alignment
b. epron-jpron-unsupervised.wfst
c. Also, accuracy will be printed
