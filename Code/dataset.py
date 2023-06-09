
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tqdm
import os 

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

def main():
    path = os.getcwd()
    df = pd.read_csv(path + "/Data/diabetes_prediction_dataset.csv")
    
    print(df.head(), "\n")
    print(" ")
    print(df.info(), "\n")
    
    # Handle duplicates
    duplicate_rows_data = df[df.duplicated()]
    print("number of duplicate rows: ", duplicate_rows_data.shape, "\n")
    df = df.drop_duplicates()
    
    # Loop through each column and count the number of distinct values
    for column in df.columns:
        num_distinct_values = len(df[column].unique())
        print(f"{column}: {num_distinct_values} distinct values")
    
    # Checking null values
    #print(df.isnull().sum())
        
    # Remove Unneccessary value [0.00195%]
    df = df[df['gender'] != 'Other']
    
    #df_sample = df.sample(n=10000, random_state=1)
    #sns.pairplot(df_sample, hue='diabetes')
    #plt.show()
    
    # Define a function to map the existing categories to new ones
    
    df['gender'] = df['gender'].replace(['Female'], '1')
    df['gender'] = df['gender'].replace(['Male'], '0')
    data = pd.get_dummies(df, columns=['smoking_history'])
    
    scaler = StandardScaler()
    df["age"] = scaler.fit_transform(df[["age"]])
    df["bmi"] = scaler.fit_transform(df[["bmi"]])
    df["blood_glucose_level"] = scaler.fit_transform(df[["blood_glucose_level"]])
    df["HbA1c_level"] = scaler.fit_transform(df[["HbA1c_level"]])
    
    y = data.pop('diabetes') 
    
    #smote = SMOTE(k_neighbors=20, n_jobs=-1)
    #x_train, y_train = smote.fit_resample(x_train, y_train)
    #
    #print("Original dataset shape %s" % Counter(y))
    #print("Resampled dataset shape %s" % Counter(y_train))
    #print(len(x_train), len(y_train))
    
    x_train, x_test, y_train, y_test = train_test_split(data, y, test_size=0.5)                
                      
    # Gradient Boosting Classifier 
    #gb = GradientBoostingClassifier(subsample=0.5)
    #grid_params_gb = {
    #                "n_estimators": [80, 90, 100, 110, 120],
    #                "learning_rate": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    #                }
    #grid = GridSearchCV(gb, grid_params_gb, cv=3, n_jobs=-1)
    #grid.fit(x_train, y_train)
    #print(grid.best_params_)
    #
    ## Random Forest Classifier
    #rf = RandomForestClassifier()
    #grid_params_rf = { "n_estimators": [300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500],
    #                    }
    #grid = GridSearchCV(rf, grid_params_rf, cv=3, n_jobs=-1)
    #grid.fit(x_train, y_train)
    #print(grid.best_params_)
    
    gb = GradientBoostingClassifier(learning_rate=0.08, n_estimators=100, subsample=0.5)
    rf = RandomForestClassifier(n_estimators=360)
    
    gb.fit(x_train, y_train), rf.fit(x_train, y_train)
    
    print("accuracy score for Gradient Boosting Classifier: {0:.2f}%".format(gb.score(x_test, y_test) * 100))
    print("accuracy score for Random Forest Classifier: {0:.2f}%".format(rf.score(x_test, y_test) * 100))
    print(" ")
    print("precision score for Gradient Boosting Classifier: {0:.2f}%".format(precision_score(y_test, gb.predict(x_test)) * 100))
    print("precision score for Random Forest Classifier: {0:.2f}%".format(precision_score(y_test, rf.predict(x_test)) * 100))
    print(" ")
    print("recall score for Gradient Boosting Classifier: {0:.2f}%".format(recall_score(y_test, gb.predict(x_test)) * 100))
    print("recall score for Random Forest Classifier: {0:.2f}%".format(recall_score(y_test, rf.predict(x_test)) * 100))
    print(" ")
    print(classification_report(y_test, gb.predict(x_test)))
    print(classification_report(y_test, rf.predict(x_test)))
    
    gb_scores = []
    rf_scores = []
    n_iterations = 100  # Number of bootstrap iterations

    # Iterating through the bootstrap iterations
    for _ in tqdm.tqdm(range(n_iterations)):
        # Create bootstrap samples for evaluation
        x_test_boot, y_test_boot = resample(x_test, y_test, replace=True)

        # Predict using the Gradient Boosting model
        gb_pred = gb.predict(x_test_boot)
        gb_accuracy = accuracy_score(y_test_boot, gb_pred)
        gb_precision = precision_score(y_test_boot, gb_pred)
        gb_recall = recall_score(y_test_boot, gb_pred)
        gb_scores.append((gb_accuracy, gb_precision, gb_recall))

        # Predict using the Random Forest model
        rf_pred = rf.predict(x_test_boot)
        rf_accuracy = accuracy_score(y_test_boot, rf_pred)
        rf_precision = precision_score(y_test_boot, rf_pred)
        rf_recall = recall_score(y_test_boot, rf_pred)
        rf_scores.append((rf_accuracy, rf_precision, rf_recall))

    # Save the results
    np.savetxt("gb_scores.csv", gb_scores, delimiter=",")
    np.savetxt("rf_scores.csv", rf_scores, delimiter=",")

    # Calculate mean and standard deviation of the scores
    gb_mean_accuracy = np.mean([score[0] for score in gb_scores])
    gb_std_accuracy = np.std([score[0] for score in gb_scores])
    gb_mean_precision = np.mean([score[1] for score in gb_scores])
    gb_std_precision = np.std([score[1] for score in gb_scores])
    gb_mean_recall = np.mean([score[2] for score in gb_scores])
    gb_std_recall = np.std([score[2] for score in gb_scores])

    rf_mean_accuracy = np.mean([score[0] for score in rf_scores])
    rf_std_accuracy = np.std([score[0] for score in rf_scores])
    rf_mean_precision = np.mean([score[1] for score in rf_scores])
    rf_std_precision = np.std([score[1] for score in rf_scores])
    rf_mean_recall = np.mean([score[2] for score in rf_scores])
    rf_std_recall = np.std([score[2] for score in rf_scores])

    # Print the results
    print("Gradient Boosting Classifier:")
    print(f"Mean Accuracy: {gb_mean_accuracy}")
    print(f"Standard Deviation Accuracy: {gb_std_accuracy}")
    print(f"Mean Precision: {gb_mean_precision}")
    print(f"Standard Deviation Precision: {gb_std_precision}")
    print(f"Mean Recall: {gb_mean_recall}")
    print(f"Standard Deviation Recall: {gb_std_recall}\n")

    print("Random Forest Classifier:")
    print(f"Mean Accuracy: {rf_mean_accuracy}")
    print(f"Standard Deviation Accuracy: {rf_std_accuracy}")
    print(f"Mean Precision: {rf_mean_precision}")
    print(f"Standard Deviation Precision: {rf_std_precision}")
    print(f"Mean Recall: {rf_mean_recall}")
    print(f"Standard Deviation Recall: {rf_std_recall}\n")

if __name__ == '__main__':
    main()