import numpy as np
import pandas as pd
from SGA_functions import *

def sga_pre_processor(csv_file, designation):
  df = pd.read_csv(csv_file)

  df = df[df['Designation'] == float(designation)]
  df = df.drop(['Designation'], axis = 1)

  df = df.drop_duplicates(subset=['Employee ID'])

  df = df.drop(["Employee ID", "Date of Joining", "Company Type", "Gender"], axis = 1)

  df['WFH Setup Available'] = df['WFH Setup Available'].map({'No': 0, 'Yes': 1})

  df = df.dropna()

  if 'Burn Rate' in df.columns:
    df = df.drop(['Burn Rate'], axis=1)

  return df

def SimpleGeneticAlgorithm(data, designation_no, no_generations, no_of_parent_samples= 10, no_crossover_points= 4, no_mutation_points= 4, no_crossover_offsprings= 5, diff_threshold= 3):
  offspring_pool_size = no_of_parent_samples
  mating_pool_size = no_of_parent_samples / 2

  parent_population = data.sample(n=no_of_parent_samples).to_numpy()

  sum_hours = sum([x[1] for x in parent_population])

  population_weights = get_feature_weights(designation_no)

  for i in range(no_generations):
    found_offspring_pool = False

    while found_offspring_pool == False:
      found_offspring_pool = False
      binary_representation = pop_to_binary(parent_population)
      parent_population_scores = cal_fitness_score(population_weights, binary_representation)

      mating_pool, mating_pool_scores = tournament_selection(binary_representation, parent_population_scores, mating_pool_size)
      offspring_pool_crossover = crossover(mating_pool, mating_pool_scores, no_crossover_points, no_crossover_offsprings, population_weights)
      offspring_pool_mutation = mutate(mating_pool, no_mutation_points, population_weights)

      unfiltered_pool = offspring_pool_crossover + offspring_pool_mutation + mating_pool
      unfiltered_pool_scores = cal_fitness_score(population_weights, unfiltered_pool)
      unfiltered_pool = pop_to_float(unfiltered_pool)
      unfiltered_pool_with_scores = [[*i,j]for i,j in zip(unfiltered_pool, unfiltered_pool_scores)]

      pool_dict_list = convert_to_dict(unfiltered_pool_with_scores)

      combinations = generate_combinations(pool_dict_list, offspring_pool_size)

      combinations_dict = combinations_to_dict(combinations)

      combinations_dict_metrics = calculate_pool_metrics(combinations_dict)

      filtered_combinations = filter_combinations_with_hours(combinations_dict_metrics, sum_hours)

      sorted_combinations = sort_combinations_by_score_and_diff(filtered_combinations)

      if cal_pop_resource_distribution(sorted_combinations, diff_threshold) == False:
        continue

      if len(sorted_combinations) != 0:
        final_pool = select_final_pool(sorted_combinations)
        found_offspring_pool = True
        population_list = pop_dict_to_list(final_pool)
        parent_population = np.array(population_list)

  total_scores = 0
  for i in final_pool['combinations']:
    total_scores = total_scores + i['score']

  mean_score = total_scores/offspring_pool_size
  print(f"mean_score: {mean_score}")

  return final_pool['combinations'], mean_score