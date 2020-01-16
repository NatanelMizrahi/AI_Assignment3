# Intro to Artificial Intelligence - Assignment3
Bayes Network for the Hurricane Evacuation problem.
Implemented with Likelihood Weighting

## How to Run:
```usage: test.py [-h] [-g GRAPH_PATH] [-T T] [-N SAMPLE_SIZE] [-s SEED]

Bayes Network for the Hurricane Evacuation Problem

optional arguments:
  -h, --help            show this help message and exit
  -g GRAPH_PATH, --graph_path GRAPH_PATH
                        path to graph initial configuration file
  -T T                  nubmer of time units for the Bayes Network
  -N SAMPLE_SIZE, --sample_size SAMPLE_SIZE
                        nubmer of samples used for the Bayes Network sampling
  -s SEED, --seed SEED  random seed for the sampling. Used for debugging

```  
### Example: 
`python3 test.py -T 2 --graph_path tests/basic.config --seed 3 --sample_size 300`

## Hurricane Evacuation Problem: Predicting the Flooding and Blockages
### Programming assignment - Reasoning under uncertainty
## Goals
Probabilistic reasoning using Bayes networks, with scenarios similar to the hurricane evacuation problem environment of programming assignment 1.

Uncertain Hurricane Evacuation Problem - Domain Description
As they try to find their best path, in the real world, evacuation forces may be unable to tell in advance where and when the Hurricane will arrive, and where flooding will occur. There may be evidence which can help, but one cannot be sure until the node and/or edge in question is reached! Not knowing the path of the hurricane makes it hard to plan an optimal path, so reasoning about the unknown is crucial. We do know that flooding tends to migrate to nearby locations, and that it has persistence, that is flooding yesterday means that flooding today is more likely.

Thus we have a binary random variable Fl(v,t) standing in for "flooding" at vertex v at time t, and a binary variable B(e,t) standing in for "blocked" for each edge e at time t. The flooding events are assumed independent, with known distributions. The blockages are noisy-or distributed given the flooding at incident vertices at the same time t, with pi =(1-qi)= 0.6*1/w(e). All noisy-or node have a leakage probability of 0.001, that is, they are true with probability 0.001 when all the causes are inactive. The leakage may be ignored for the cases where any of the causes are active.

Flooding probabilities P(Fl(v,0)=true) at vertices for time 0 are provided in the input. For subesquent times (t=1,2, etc.) they are dependent only on the occurence of flooding at the previous time slice, we will have: P(Fl(v,t+1)=true |Fl(v,t)=true))=Ppersistence, where Ppersistence is a user-determined constant (usually between 0.7 and 0.99),and P(Fl(v,t+1)=true |Fl(v,t)=false))=P(Fl(v,0)=true). Such a network of variables indexed by time, that aims at modeling the dynamics of the world, is sometimes called a Dynamic Bayes Network (DBN).

All in all, you have 2 types of variables (BN nodes): blockages (one for each edge and time unit) flooding (one for each vertex, and time unit).

In your program, a file specifies the geometry (graph), and parameters such as P(Fl(v)=true)). Then, you enter some locations where flooding and blockages are reported either present or absent (and the rest remain unknown). This is the evidence in the problem. Once evidence is instantiated, you need to perform reasoning about the likely locations of flooding, blockages, and evacuees (all probabilities below "given the evidence"):

* What is the probability that each of the vertices is flooded?
* What is the probability that each of the edges is blocked?
* What is the probability that a certain path (set of edges) is free from blockages? (Note that the distributions of blockages in edges are NOT necessarily independent.)
* What is the path between 2 given vertices that has the highest probability of being free from blockages at time t=1 given the evidence? (bonus)
Input can be as an ASCII file, similar to graph descriptions in previous assignments, for example:
```
#N 4                 ; number of vertices n in graph (from 1 to n)
#V1 F 0.2            ; Vertex 1, probability of flooding 0.2 at t=0
#V2 F 0.4            ; Vertex 2, probability of flooding 0.4 at t=0
                     ; Either assume flooding probability 0 by default,
                     ; or make sure to specify this probability for all vertices.
#Ppersistence 0.9    ; Set persistence probability to 0.9
#E1 1 2 W1           ; Edge1 between vertices 1 and 2, weight 1
#E2 2 3 W3           ; Edge2 between vertices 2 and 3, weight 3
#E3 3 4 W3           ; Edge3 between vertices 3 and 4, weight 3
#E4 2 4 W4           ; Edge4 between vertices 2 and 4, weight 4
```

## Requirements
### Part I
Your program should read the data, including the distribution parameters, which are defined as above. The program should construct a Bayes network according to the scenario, for at least 2 time slices: t=0 and t=1. The program should also allow for an output of the Bayes network constructed for the scenario.

For example, part of the output for the above graph, would be:

```
VERTEX 1, time 0:
  P(Flooding) = 0.2
  P(not Flooding) = 0.8
VERTEX 2:
etc.
EDGE 1, time 0:
  P(Blocakge 1 | not flooding 1, not flooding 2) = 0.001
  P(Blocakge 1 | flooding 1, not flooding 2) = 0.6
  P(Blocakge 1 | not flooding 1, flooding 2) = 0.6
  P(Blocakge 1 | flooding 1, flooding 2) = 0.84
etc.
```
### Part II 
After the network is fully constructed, you should support querying the user for a set of evidence. We do this by reading one piece of evidence at a time (e.g. "Flood reported at vertex 2 at time 0", and then "No blockage reported at edge 1 at time 0" etc.). The online interactive operations your program should support are:

Reset evidence list to empty.
Add piece of evidence to evidence list.
Do probabilistic reasoning (1, 2, 3), or (1,2,3,4), whichever your program supports, and report the results.
Quit.
Probabilistic reasoning should be done in order to answer the questions on distribution of blockages, etc., and report on the answers, including all the posterior probabilities. You may use any algorithm in the literature that supports solution of BNs, including simple enumerarion, variable elimination, polytree propagation, or sampling.