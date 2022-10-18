from flask import Flask,jsonify,request
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

from sklearn.pipeline import Pipeline


def add(old,new_df) :
    appended_df = pd.concat([old,new_df],ignore_index=True)
    return appended_df
### MUST RETRIEVE ALL POSSIBLE CHAMP TAGS BEFORE BEING ABLE TO ONE HOT ENCODE. 
# ONE POSSIBLE SOLUTION IS TO ADD DUMMY DATA FOR WHICH IT WOULD HELP GENERATE THE ONE HOT ENCODE VALUE FOR EACH CHAMPION TAG FOR EACH CATEGORICAL FEATURE IN THE DATASET (6 CHAMP TAGS -> 6 EXTRA DUMMY ROWS, 1 FOR EACH CHAMP TAG)
def fill_missing_champ_tags_with_dummy(df): 
    columns = list(df.columns)
    champ_name_columns = [c for c in columns if c.startswith('team_comp') or c.startswith('dmg_carry') or c.startswith('obj_carry')]
    unique_champ_tags = df[champ_name_columns].stack().unique()
    dummy_dict = {}
    for k in champ_name_columns :
        dummy_dict[k] = unique_champ_tags.copy()
    dummy_df = pd.DataFrame(dummy_dict)
    dummy_df = dummy_df.replace(np.nan,0)
    extra_rows = dummy_df.shape[0]
    print('Number of extra dummy rows = ',extra_rows)
    df = add(df,dummy_df)
    return (df,extra_rows)

def prepare_data_for_prediction(df) :
    columns = list(df.columns)
    champ_name_columns = [c for c in columns if c.startswith('team_comp') or c.startswith('dmg_carry') or c.startswith('obj_carry')]
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



app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to LoL team comp winner predictor"

@app.route('/predict', methods=['POST'])
def predict():
     json_ = request.json
     df = pd.DataFrame(json_)
     return jsonify({'prediction': json_})


if __name__ == '__main__':
    app.run(debug=True)