import pandas as pd

def sga_pre_processor(csv_file, designation):
  df = pd.read_csv(csv_file)

  df = df[df['Designation'] == float(designation)]
  df = df.drop(['Designation'], axis = 1)

  df = df.drop_duplicates(subset=['Employee ID'])

  df = df.drop(["Employee ID", "Date of Joining", "Company Type", "Gender"], axis = 1)

  df['WFH Setup Available'] = df['WFH Setup Available'].map({'No': 0, 'Yes': 1})

  df = df.dropna()

  df = df.drop(['Burn Rate'], axis = 1)

  return df