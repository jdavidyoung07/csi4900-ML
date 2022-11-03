import json
import sys
from flask import Flask,jsonify,request
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import traceback
import dill
from flask_cors import cross_origin


champ_data = {}
with open('../champion_data/champion.json','r',encoding='utf-8') as f :
    champions = json.load(f)
    for champion in champions['data'] :
        champ_data[str.lower(champion)] = champions['data'][champion]

def champ_name_replacer(champ_name) :
    return champ_data[str.lower(champ_name)]['tags'][0]

    

def add(old,new_df) :
    appended_df = pd.concat([old,new_df],ignore_index=True)
    return appended_df

### MUST RETRIEVE ALL POSSIBLE CHAMP TAGS BEFORE BEING ABLE TO ONE HOT ENCODE. 
# ONE POSSIBLE SOLUTION IS TO ADD DUMMY DATA FOR WHICH IT WOULD HELP GENERATE THE ONE HOT ENCODE VALUE FOR EACH CHAMPION TAG FOR EACH CATEGORICAL FEATURE IN THE DATASET (6 CHAMP TAGS -> 6 EXTRA DUMMY ROWS, 1 FOR EACH CHAMP TAG)
def fill_missing_champ_tags_with_dummy(df): 
    columns = list(df.columns)
    champ_name_columns = [c for c in columns if c.startswith('team_comp') or c.startswith('dmg_carry') or c.startswith('obj_carry')]
    unique_champ_tags = ['Marksman', 'Fighter','Mage','Tank','Assassin','Support']
    dummy_dict = {}
    for k in champ_name_columns :
        dummy_dict[k] = unique_champ_tags.copy()
    dummy_df = pd.DataFrame(dummy_dict)
    dummy_df = dummy_df.replace(np.nan,0)
    extra_rows = dummy_df.shape[0]
    print('Number of extra dummy rows = ',extra_rows)
    df = add(df,dummy_df)
    return (df,extra_rows)

def prepare_team_comp_data_for_prediction(df) :
    columns = list(df.columns)
    champ_name_columns = [c for c in columns if c.startswith('team_comp') or c.startswith('dmg_carry') or c.startswith('obj_carry')]

    for c in champ_name_columns :
        df[c] = df[c].apply(lambda x : champ_name_replacer(x))
    
    X,dummy_rows_len = fill_missing_champ_tags_with_dummy(df)

    num_pipeline = Pipeline([
        ('std_scaler',StandardScaler())
    ])

    full_column_set,cat_column_set = set(list(X.columns)),set(champ_name_columns)
    num_columns = list(full_column_set - cat_column_set)

    full_pipeline = ColumnTransformer([
            ('num',num_pipeline,num_columns),
            ("cat", OneHotEncoder(), champ_name_columns),
        ],remainder='passthrough')

    X_prepared = full_pipeline.fit_transform(X)
    size = X_prepared.shape[0]
    X_prepared = X_prepared[:size-dummy_rows_len]
    return X_prepared

def prepare_no_comp_data_for_prediction(df) :
    num_pipeline = Pipeline([
        ('std_scaler',StandardScaler())
    ])

    full_column_set = set(list(df.columns))
    num_columns = list(full_column_set)

    full_pipeline = ColumnTransformer([
            ('num',num_pipeline,num_columns),
        ],remainder='passthrough')

    df_prepared = full_pipeline.fit_transform(df)
    size = len(df)
    df_prepared = df_prepared[:size]

    return df_prepared


app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to LoL team comp winner predictor"

@app.route('/predict/no_comp', methods=['POST'])
@cross_origin()
def predict_no_comp():
    model_no_comp = joblib.load("../models/model_noteam_comp_svc.pkl") # Load "model.pkl"
    if model_no_comp:
        try:
            json_ = request.json
            print(json_)
            query = pd.DataFrame(json_)
            prepared_query = prepare_no_comp_data_for_prediction(query)
            prediction = list(model_no_comp.predict(prepared_query))
            print(prediction)
            return jsonify({'prediction': int(prediction[0])})
        except:
            return jsonify({'trace': traceback.format_exc()})
    else:
        print ('Train the no comp model first')
        return ('No non-comp model here to use')

@app.route('/predict/team_comp', methods=['POST'])
@cross_origin()
def predict_team_comp():
    model_team_comp = joblib.load("../models/model_team_comp_svc.pkl") # Load "model.pkl"
    if model_team_comp:
        try:
            json_ = request.json
            print(json_)
            query = pd.DataFrame(json_)
            prepared_query = prepare_team_comp_data_for_prediction(query)
            prediction = list(model_team_comp.predict(prepared_query))
            print(prediction)
            return jsonify({'prediction': int(prediction[0])})
        except:
            return jsonify({'trace': traceback.format_exc()})
    else:
        print ('Train the team comp model first')
        return ('No team comp model here to use')

model_no_comp = None
model_team_comp = None
if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except:
        port = 12345 

    app.run(port=port, debug=True)