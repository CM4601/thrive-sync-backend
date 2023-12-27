import numpy as np
from flask_cors import CORS
from flask import Flask, request, jsonify
import pandas as pd
from model_loader import loader
from error_handler import *
from SGA import sga_pre_processor, SimpleGeneticAlgorithm
from func_timeout import func_timeout, FunctionTimedOut

# Iniatlize a Flask app
app = Flask('app')
CORS(app, resource={r"/api/*": {"origins": "*"}})
app.config['CORS HEADERS'] = 'content-Type'


# Load the models from the pickle files
model_des_0, model_des_1, model_des_2, model_des_3, model_des_4, model_des_5 = loader('models')
print("Models Loaded Successfully")

@app.route('/api/predictBurnOut', methods=['POST'])
def burn_out_predict():
  try:
    # get the JSON data from the request body
    json_data = request.json

    # Raise relevant errors if any data is missing
    if 'Designation' not in json_data:
      raise NoDesignationError
    if 'WFH Setup Available' not in json_data:
        raise NoWFHSetupAvailabilityError
    if 'Resource Allocation' not in json_data:
        raise NoResourceAllocationError
    if 'Mental Fatigue Score' not in json_data:
        raise NoMentalFatigueScoreError

    designation = int(json_data.get('Designation'))
    wfh_availability = 1 if str(json_data.get('WFH Setup Available')) ==  'Yes' else -1
    resource_allocation = float(json_data.get('Resource Allocation'))
    mental_fatigue_score = float(json_data.get('Mental Fatigue Score'))

    if designation == 0:
      model = model_des_0
    elif designation == 1:
      model = model_des_1
    elif designation == 2:
      model = model_des_2
    elif designation == 3:
      model = model_des_3
    elif designation == 4:
      model = model_des_4
    elif designation == 5:
      model = model_des_5
    
    new_data = np.array([[wfh_availability, resource_allocation, mental_fatigue_score]])
    prediction = model.predict(new_data)

    if prediction:
      return jsonify({ "status": 200, "prediction": prediction[0] })
    else:
      return jsonify({ "status": 400, "messege": "Response failed at backend" })
    
  except NoDesignationError as des:
    return jsonify({"status": 500, "message": str(des)})
  
  except NoWFHSetupAvailabilityError as wfh:
    return jsonify({"status": 500, "message": str(wfh)})

  except NoResourceAllocationError as ra:
    return jsonify({"status": 500, "message": str(ra)})
  
  except NoMentalFatigueScoreError as mfs:
    return jsonify({"status": 500, "message": str(mfs)})
  
@app.route('/api/generateTeam', methods=['POST'])
def generate_team():
    try:
      csv_file = request.files['csv_file']
      designation = int(request.form['Designation'])
      no_generations = int(request.form['Number of generations'])

      if 'csv_file' not in request.files:
        raise NoCSVFileError
      
      if 'Designation' not in request.form:
        raise NoDesignationError
      
      if 'Number of generations' not in request.form:
        raise NoNumGenerationsError
      
      pre_processed_data = sga_pre_processor(csv_file= csv_file, designation= designation)
      try:
        respone = func_timeout(6, SimpleGeneticAlgorithm, args=(pre_processed_data, designation, no_generations))
        return jsonify({ "status": 200, "respone": respone })
      
      except FunctionTimedOut:
        return jsonify({"message": "Function timed out after 1 minute."}), 504
    
    except NoCSVFileError as csv:
      return jsonify({"status": 500, "message": str(csv)})

    except NoDesignationError as des:
      return jsonify({"status": 500, "message": str(des)})
    
    except NoNumGenerationsError as nog:
      return jsonify({"status": 500, "message": str(nog)})

# Run the app
if __name__ == '__main__':
    app.run()