import numpy as np
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from model_loader import loader
from error_handler import NoDesignationError, NoWFHSetupAvailabilityError, NoResourceAllocationError, NoMentalFatigueScoreError, NoCSVFileError

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
      return jsonify({ "status": 200, "prediction": prediction })
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

      if 'csv_file' not in request.files:
        raise NoCSVFileError
      
      if 'Designation' not in request.form:
        raise NoDesignationError
      
      respone = [
        [-1.0, 7.0, 6.1],
        [1.0, 4.0, 6.0],
        [1.0, 6.0, 7.6],
        [-1.0, 8.0, 8.3],
        [-1.0, 5.0, 6.8],
        [1.0, 8.0, 7.5],
        [-1.0, 4.0, 6.3],
        [-1.0, 6.0, 6.5],
        [-1.0, 5.0, 5.9],
        [-1.0, 8.0, 8.2],
        [1.0, 6.0, 7.5],
        [1.0, 6.0, 9.1],
        [-1.0, 5.0, 7.6],
        [-1.0, 6.0, 8.2],
        [1.0, 5.0, 6.6],
        [-1.0, 5.0, 6.9],
        [-1.0, 5.0, 4.7],
        [1.0, 7.0, 8.5],
        [1.0, 7.0, 7.2],
        [-1.0, 4.0, 3.3]
      ]

      return jsonify({ "status": 200, "respone": respone })
    
    except NoCSVFileError as csv:
      return jsonify({"status": 500, "message": str(csv)})

    except NoDesignationError as des:
      return jsonify({"status": 500, "message": str(des)})

# Run the app
if __name__ == '__main__':
    app.run()