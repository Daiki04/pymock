import random

import numpy as np
from deap import base

from classes import MOCKGenotype

def uniform_xover(parent1, parent2, cxpb):
    """Uniform crossover
    
    Arguments:
        parent1 {DEAP individual} -- First parent
        parent2 {DEAP individual} -- Second parent
        cxpb {float} -- Probability of undergoing crossover
    
    Returns:
        [type] -- [description]
    """
    # Below not really necessary
    assert len(parent1) == len(parent2)
    # Make copies of the parents
    child1 = parent1[:]
    child2 = parent2[:]
    # Test if we undergo crossover
    if cxpb == 1:
        for i in range(len(parent1)):
            if random.random() < 0.5:
                parent1[i] = child1[i]
                parent2[i] = child2[i]
            else:
                parent1[i] = child2[i]
                parent2[i] = child1[i]
        # Caveat: there is a 0.5**len(parent1) chance the parents will be equal to children
        del parent1.fitness.values, parent2.fitness.values
    # In case another probability is used; we avoid a random.random() call in normal case
    elif random.random() <= cxpb:
        for i in range(len(parent1)):
            if random.random() < 0.5:
                parent1[i] = child1[i]
                parent2[i] = child2[i]
            else:
                parent1[i] = child2[i]
                parent2[i] = child1[i]
        del parent1.fitness.values, parent2.fitness.values
    # If we change cxpb to be <1 then we may not enter loop, so return unchanged
    # We'll keep their fitnesses so we don't need to re-evaluate (unless mutation changes)
    return parent1, parent2

def neighbour_mut(parent, MUTPB, gen_length, argsortdists, L, interest_indices, nn_rankings):
    """Neighbourhood-biased mutation operator
    
    Arguments:
        parent {DEAP individual} -- The genotype
        MUTPB {float} -- Mutation probability threshold
        gen_length {int} -- Equal to reduced_length when delta>0, or N otherwise
        argsortdists {np.array} -- Argsort of the distance array
        L {int} -- Neighbourhood hyperparameter
        interest_indices {list} -- Indices of the most interesting links
        nn_rankings {np.array} -- Nearest neighbour rankings for every datapoint
    
    Returns:
        parent {DEAP individual} -- The mutated genotype
    """
    # Calculate the first term of the mutation equation
    first_term = (MUTPB / gen_length)
    # Using a comprehension for this bit is faster
    mutprobs = [
        first_term +
        ((nn_rankings[interest_indices[index]][value] / gen_length) ** 2)
        for index, value in enumerate(parent)
    ]
    # Now just loop over the probabilities
    # As we're using assignment, can't really do this part in a comprehension!
    for index, mutprob in enumerate(mutprobs):
        if random.random() < mutprob:
            parent[index] = MOCKGenotype.replace_link(
                argsortdists, interest_indices[index], parent[index], L
            )
    return parent

def comp_centroid_mut(parent, MUTPB, gen_length, argsortdists_cen, L_comp, interest_indices, nn_rankings_cen, data_dict):
    first_term = (MUTPB / gen_length)
    # Using a comprehension for this bit is faster
    mutprobs = [
        first_term +
        ((nn_rankings_cen[data_dict[index].base_cluster_num][data_dict[value].base_cluster_num] / gen_length) ** 2)
        for index,value in enumerate(parent)
    ]
    # Now just loop over the probabilities
    # As we're using assignment, can't really do this part in a comprehension!
    for index, mutprob in enumerate(mutprobs):
        if random.random() < mutprob:
            parent[index] = MOCKGenotype.centroid_replace_link(
                argsortdists_cen, interest_indices[index], parent[index], L_comp, data_dict
            )
    return parent

def neighbour_comp_mut(parent, MUTPB, gen_length, interest_indices, nn_rankings, component_nns, data_dict):
    first_term = (MUTPB / gen_length)
    mutprobs = [
        first_term +
        ((nn_rankings[interest_indices[index]][value] / gen_length) ** 2)
        for index,value in enumerate(parent)
    ]
    for index, mutprob in enumerate(mutprobs):
        if random.random() < mutprob:
            parent[index] = MOCKGenotype.neighbour_replace_link(
                component_nns, interest_indices[index], parent[index], data_dict
            )
    return parent