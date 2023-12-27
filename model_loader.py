import os
import pickle

def loader(folder_path):
  # Get a list of all files in the specified folder
  all_files = os.listdir(folder_path)
  
  # Filter files to include only those with ".pkl" extension
  model_filenames = [file for file in all_files if file.endswith(".pkl")]

  # Dictionary to store loaded models
  loaded_models = {}

  # Load each model from its corresponding pickle file
  for filename in model_filenames:
      file_path = os.path.join(folder_path, filename)
      with open(file_path, "rb") as file:
          loaded_model = pickle.load(file)
          loaded_models[filename] = loaded_model

  # Return the loaded models
  return tuple(loaded_models.values())