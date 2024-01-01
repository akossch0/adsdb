import pandas as pd
import duckdb
import pickle
import os
import time


def get_predictions(model, test_df: pd.DataFrame, trace_df: pd.DataFrame):
    pred_df = model.predict(test_df[trace_df.predictors[0]])
    pred_df["prediction"] = list(pred_df.idxmax(axis=1) + 1)
    return pred_df


print("Loading model training data from tracing db for model reconstruction.")
con = duckdb.connect("datasets/trace/data-governance.db")
trace_df = con.execute("select * from model_training").df()
print("Model training data loaded.")
con.close()

print("Loading model from pickle file.")
model_path = "datasets/predict/model/model.pkl"
with open(model_path, "rb") as f:
    model = pickle.load(f)
print("Model loaded.")


input_dir = "datasets/predict/input"
files = os.listdir(input_dir)
csv_files = [f for f in files if f.endswith(".csv")]

if csv_files:
    latest_file = max(
        csv_files, key=lambda f: os.path.getmtime(os.path.join(input_dir, f))
    )
    file_path = os.path.join(input_dir, latest_file)
    df = pd.read_csv(file_path)
else:
    print("No .csv files found in the directory.")

print("Running predictions on {}.".format(file_path))
pred_df = get_predictions(model, df, trace_df)

output_dir = "datasets/predict/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

timestamp_millis = str(int(time.time() * 1000))
output_filename = latest_file[:-4] + "_predictions_" + str(timestamp_millis) + ".csv"
output_path = os.path.join(output_dir, output_filename)
pred_df.to_csv(output_path, index=False)
print("Predictions saved to {}.".format(file_path[:-4] + "_predictions.csv"))
