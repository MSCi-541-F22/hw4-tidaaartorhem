# hw4-tidaaartorhem
hw4-tidaaartorhem created by GitHub Classroom

# AADIT MEHROTRA 20756049 Assignment 4 

The Code is for Problem 7 of the assignment 

Step 1 -->  is to generate the stem and baseline txt files from indexEngine.py 
  (Make sure the latimes.gz file is in the root folder and always create the documents folder named 'documents' for baseline
  and 'documentsStem' for stem in the root as shown below)

  --> Part 1 for baseline --> python3 indexEngine.py ./latimes.gz ./documents 
  
  --> Part 2 for Stem  --> python3 indexEngine.py ./latimes.gz  ./documentsStem --stem=true

Step 2 --> By now the 2 folders of documents and documentsStem should be there in the root. We will now generate 
  the hw4-bm25-stem-asmehrot.txt and hw4-bm25-baseline-asmehrot.txt files using bm25.py 
  (Note: the queries.txt file is being used as queries.p and is present in the root folder and hard coded in the bm25.py file on line 75)
  Ensure the queries.p file is present in the root folder when running the following command 
  
  --> Part 1 for baseline --> python3 bm25.py ./documents 
  
  --> Part 2 for Stem --> python3 bm25.py ./documentsStem --stem=true 
  
 Step 3 --> By now the root folder should have these 2 files -- hw4-bm25-stem-asmehrot.txt and hw4-bm25-baseline-asmehrot.txt. 
            In this step we will use evaluate to generate the scores. 
           
           Part 1 --> To generate the Precision Scores in csv form for both stem and baseline 
                put these 2 files in a directory in the root folder called results-files and then run this --
                
   python3 evaluate.py --qrel=./qrels/LA-only.trec8-401.450.minus416-423-437-444-447.txt --output_directory=./ --results=results-files/
   
   -------Now you should get in the root folder you should have these files 
      ------------  average_measures.csv -- performance using the same effectiveness measures used in HW 3
      ------------  summary_statistics.csv -- statistical significance testing
      -----------   hw4-bm25-baseline-asmehrot.csv -- precision scores for baseline 
      -----------   hw4-bm25-baseline-asmehrot.csv -- precision scores for stem 
      
 Step 4 Lastly to compare the baseline vs the stem you can run this command to generate a compare.csv file that would have the intended comparison between the different metrics of scoreX that is baseline and score y that is stem  

 python3 evaluate.py --qrel=./qrels/LA-only.trec8-401.450.minus416-423-437-444-447.txt --output_directory=./ --results_files results-files/hw4-bm25-baseline-asmehrot.txt results-files/hw4-bm25-stem-asmehrot.txt    --compare ./hw4-bm25-baseline-asmehrot.csv ./hw4-bm25-stem-asmehrot.csv


  
