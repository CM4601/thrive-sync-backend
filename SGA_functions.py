import random
import numpy as np
from itertools import combinations

def get_feature_weights(des_num):
  feature_weights_list = np.load('feature_weights.npy', allow_pickle=True)
  return feature_weights_list[des_num]

def float_to_binary(value, integer_bits, decimal_bits):
  # Convert the floating-point number to binary
  integer_part = int(value)
  decimal_part = value - integer_part

  # Convert the integer part to binary with the specified number of bits
  integer_representation = bin(integer_part)[2:].zfill(integer_bits)

  # Convert the decimal part to binary with the specified number of bits
  decimal_representation = ''
  for _ in range(decimal_bits):
    decimal_part *= 2
    if decimal_part >= 1:
      decimal_representation += '1'
      decimal_part -= 1
    else:
      decimal_representation += '0'
  binary_representation = str(integer_representation) + str(decimal_representation)

  # Combine the integer and decimal parts

  return binary_representation

def pop_to_binary(population):
  binary_population = []
  for record in population:
    binary_representations = float_to_binary(record[0], 1, 0) + float_to_binary(record[1], 4, 0) + float_to_binary(record[2], 4, 4)
    binary_population.append(binary_representations)

  binary_2d_array = [[int(digit) for digit in binary_str] for binary_str in binary_population]

  return binary_2d_array

def binary_to_float(binary_record):
    wfh_status = binary_record[0]
    hours_allocated = binary_record[1:5]
    fatigue_score = binary_record[5:]

    #decoding wfh status to original scenario.
    if wfh_status == 0:
      wfh_status = -1

    #decoding hours allocated
    hours_allocated =  int("".join(map(str, hours_allocated)), 2)

    #for fatigue score decoding
    whole_number_bits = fatigue_score[:-4]
    real_value_bits = fatigue_score[-4:]

    whole_number = int("".join(map(str, whole_number_bits)), 2)
    real_value = sum(bit * 2**(-i-1) for i, bit in enumerate(real_value_bits))

    fatigue_score = whole_number + real_value

    decimal_record = [wfh_status, hours_allocated, fatigue_score]

    return decimal_record

def cal_fitness_score(feature_weights, population):
  scores = []
  for record in population:
    decimal_record = binary_to_float(record)

    wfh_val = feature_weights[0] * decimal_record[0]
    hours_allocated_val = feature_weights[1] * decimal_record[1]
    fatigue_val = feature_weights[2] * decimal_record[2]
    bias = feature_weights[3]

    fitness_val = wfh_val + hours_allocated_val + fatigue_val + bias
    scores.append(fitness_val)
  scores_scaled = [1 if x > 1 else x for x in scores]
  scores_scaled = [0 if x < 0 else x for x in scores]

  return scores_scaled

def tournament_selection(population, scores, num_selected):
  population_copy = population.copy()
  scores_copy = scores.copy()

  selected_individuals = []
  selected_individual_score = []

  while len(selected_individuals) < num_selected:
    # print(len(population_copy))
    if len(population) < 2:
      break

    group_indices = random.sample(range(len(population_copy)), 2)
    group = [(population_copy[i], scores_copy[i]) for i in group_indices]

    # Get the best individual from the group based on fitness scores
    winner = max(group, key=lambda x: x[1])[0]
    winner_score = max(group, key=lambda x: x[1])[1]

    selected_individuals.append(winner)
    selected_individual_score.append(winner_score)

    # remove the selected individual from the population and fitness scores
    index_to_remove = group_indices[group.index((winner, max(group, key=lambda x: x[1])[1]))]
    population_copy.pop(index_to_remove)
    scores_copy.pop(index_to_remove)

  return selected_individuals, selected_individual_score

def roulette_wheel_select(population, scores, num_selected):
  total_fitness = sum(scores)
  selection_probabilities = [score / total_fitness for score in scores]

  selected_pairs = []

  for _ in range(num_selected):
    # Spin the roulette wheel to select two individuals
    selected_individuals = []
    for _ in range(2):
      rand_value = random.random()
      cumulative_prob = 0

      for i, prob in enumerate(selection_probabilities):
        cumulative_prob += prob
        if rand_value <= cumulative_prob:
          selected_individuals.append(population[i])
          break

    selected_pairs.append(selected_individuals)

  return selected_pairs

def pop_to_float(binary_population):
  unfiltered_pool = []

  for i in binary_population:
    unfiltered_pool.append(binary_to_float(i))

  return unfiltered_pool

def individual_fitness_score(feature_weights, record):
  wfh_val = feature_weights[0] * record[0]
  hours_allocated_val = feature_weights[1] * record[1]
  fatigue_val = feature_weights[2] * record[2]
  bias = feature_weights[3]

  fitness_val = wfh_val + hours_allocated_val + fatigue_val + bias

  return fitness_val

def constraints(record, feature_weights, selected_pool):
  record = binary_to_float(record)
  score = individual_fitness_score(feature_weights, record)

  if (record[0] == -1) or (record[0] == 1):
    if (record[1] > 0) and (record[1] <= 10):
      if (record[2] >= 0) and (record[2] <= 10):
        if (score > 0) and (score < 1):
          if record not in selected_pool:
            return True
              
  return False

def crossover(selected_pool, selected_pool_scores, num_points, num_offsprings, feature_weights):
  offspring_count = 0
  offspring_pool = []
  while (offspring_count < num_offsprings):
    mating_pairs = roulette_wheel_select(selected_pool, selected_pool_scores, 1)
    parent1 = mating_pairs[0][0]
    parent2 = mating_pairs[0][1]

    crossover_points = sorted(np.random.choice(len(parent1), num_points, replace=False))
    offspring = parent1.copy()

    for i in range(len(crossover_points) - 1):
      if i % 2 == 1:
        offspring[crossover_points[i]:crossover_points[i+1]] = parent2[crossover_points[i]:crossover_points[i+1]]

    float_selected_pool = pop_to_float(selected_pool)
    offspring_validity = constraints(offspring, feature_weights, float_selected_pool)

    if offspring_validity == False:
      continue

    offspring_count += 1
    offspring_pool.append(offspring)

  return offspring_pool

def mutate(selected_pool, num_points, feature_weights):
  valid = False
  mutated_pool = []
  for individual in selected_pool:
    valid = False
    while valid == False:
      mutated_individual = individual.copy()
      mutation_points = np.random.choice(len(mutated_individual), num_points, replace=False)

      for point in mutation_points:
        mutated_individual[point] = 1 - mutated_individual[point]

      valid = constraints(mutated_individual, feature_weights, pop_to_float(selected_pool))
    mutated_pool.append(mutated_individual)

  return mutated_pool

def convert_to_dict(unfiltered_pool_with_scores):
  pool_dict_list = {}

  for index, i in enumerate(unfiltered_pool_with_scores):
    temp = {}
    temp['wfh'] = i[0]
    temp['hours'] = i[1]
    temp['fatigue'] = i[2]
    temp['score'] = i[3]
    pool_dict_list[index] = temp

  return pool_dict_list

def generate_combinations(pool, comb_no):
  all_combinations = list(combinations(pool.values(), comb_no))
  return all_combinations

def combinations_to_dict(all_combinations):
  all_dicts = []

  for i, comb in enumerate(all_combinations):
    temp = { 'combinations' : [] }

    for j, genome in enumerate(comb):
      temp['combinations'].append(genome)

    all_dicts.append(temp)

  return all_dicts

def calculate_pool_metrics(all_dicts):
  for comb in all_dicts:
    total_hours, total_score, mean_score, min_hours, max_hours, hour_diff = 0, 0, 0, 10, 0, 10

    for genome in comb['combinations']:
      total_hours += genome['hours']
      total_score += genome['score']
      min_hours = genome['hours'] if genome['hours'] < min_hours else min_hours
      max_hours = genome['hours'] if genome['hours'] > max_hours else max_hours

    mean_score = total_score/10
    hour_diff = max_hours - min_hours

    comb['diff'] = hour_diff
    comb['mean_score'] = mean_score
    comb['total_hours'] = total_hours

  return all_dicts

def filter_combinations_with_hours(combinations, no_of_hours):
  filtered_combinations = []

  for pool in combinations:
    if pool['total_hours'] == no_of_hours:
      filtered_combinations.append(pool)

  return filtered_combinations

def sort_combinations_by_score_and_diff(combinations):
  return sorted(combinations, key=lambda x: (x['diff']/x['mean_score']), reverse=True)

def cal_pop_resource_distribution(population, diff_threshold):
  genome_diff_exceeds = True

  for genome in population:
    if genome["diff"] > diff_threshold:
      genome_diff_exceeds = False

  return genome_diff_exceeds

def select_final_pool(combinations):
  return combinations[0]

def pop_dict_to_list(pop_dict):
  pop_list = []
  for dict in pop_dict['combinations']:
    temp = []
    temp.append(dict['wfh'] if dict['wfh'] == 1 else 0)
    temp.append(dict['hours'])
    temp.append(dict['fatigue'])
    pop_list.append(temp)

  return pop_list