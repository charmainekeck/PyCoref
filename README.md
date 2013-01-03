Coref
=====

Final Project for CS 5340 / 6340, Coreference Resolution

###Authors

* Adam Walz

* Charmaine Keck

Uncompressing
-------------
This project is compressed in a .tar.gz file due to the handin utility not
allowing students to hand in a file structure.

To uncompress run 

	tar -xvzf coref.tar.gz
	cd final

Usage with Makefile
--------------------
A Makefile was added to allow the easy configuration and running of this
project. Its purpose is to point to a specific python installation
(python 2.7.3) as well as datasets used for the python natural language
toolkit (nltk). Running the make command ***will run the entire project and 
place output files in the desired output directory***.

As arguments, pass ```make``` the paths to the listfile and output directory

	make ARGS="listfile output_dir"

###Example
Given that the listfile is at:
```/home/cs5340/Project/DryRun/testset1/filelist2```

And the output directory is:
```/home/cs5340/Project/DryRun/Results/output/```

The make command would be
```make ARGS="/home/cs5340/Project/DryRun/testset1/filelist2 /home/cs5340/Project/DryRun/Results/output/"```

This both configures and runs the project, and places the results in the output
directory

Usage without Makefile
------------------------
This is not recommended due to different versions of python on the cade machines

Running the help command ```python coref.py -h``` prints

	Coreference Resolution Engine
	
	positional arguments:
	listfile              File containing file path strings
	responsedir           Path to output directory
	
	optional arguments:
	-h, --help            show this help message and exit
	-v, --verbose         increase output verbosity
	-t, --test            run doctests only
	-H HOST, --host HOST  Host address of stanford corenlp server
	
	Satisfies final project for CS 5340/6340, University of Utah 
	AUTHORS: Adam Walz (walz), Charmaine Keck (ckeck)
	
	For more information, please see project
	description http://www.eng.utah.edu/~cs5340/project/project.pdf
