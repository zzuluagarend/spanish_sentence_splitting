# Spanish Sentence Splitting

The aim of this set of scripts is to take as input one Spanish file in the NewsScape dataset and return an XML-style file with one sentence per line. POS tagging and dependency information is not yet available. 

## How to run:

### preprocess.py 

This script takes as input a NewsScape text file and extract unnecessary information. The output is a text file with header information. Currently, the ocurrence time of each block is not properly treated by the main script. 

Usage: `python3 preprocess.py <input-file-name> -t <0 (recommended) or 1>`

### ss.rb

This script needs ruby and the package "pragmatic_segmenter". It takes a body of text and the corresponding language (two letters acording to the [ISO 639-1](https://www.tm-town.com/languages) code). It returns one sentence per line. anthe output of the preprocess.py script and returns 

Usage: `cat <input-file-name> | ruby ss.rb <language-code>`


### metadata.py

This script takes the output from ss.rb and returns a well-formed XML file with one sentence.

Usage: `python3 metadata.py <input-file-name>`



Currently, a pipeline command is not available. 

 