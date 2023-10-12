# mbase

An algorithm for discovering minimal hitting sets.

# Description

In the context of this algorithm, a hitting set pertaining to a collection of sets 'N' defined over domain 'M' can be described as a set of elements within 'M' that exhibits non-empty intersections with every set in 'N.'

The algorithm specifically focuses on identifying minimal hitting sets, which are hitting sets 'S' with the unique property that no subset of 'S' can function as a hitting set in its own right.

The script performs two distinct runs for each input file. The first run executes the algorithm without any preprocessing applied to the input data. Subsequently, the second run employs the algorithm in conjunction with some preprocessing applied to the input data. This sequence of runs facilitates a comparative analysis of execution times, clearly demonstrating the advantages of preprocessing the input data in terms of performance improvement.

This project includes two archives: "benchmarks1.zip" and "benchmarks2.zip," each containing a selection of sample input files.

Command line arguments are described in the command line help.

# TODO

- Add command line switch controlling whether to perform both runs or just the optimized one
- Add translations