from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, recall_score, precision_score
import pandas as pd
import mlflow
import mlflow.xgboost
##import dagshub
##dagshub.init(repo_owner='Kwamenas', repo_name='E2Enectsecurity', mlflow=True)


def get_classification_score(y_true, y_preds):
    try:
        return {
            "f1": f1_score(y_true, y_preds),
            "recall": recall_score(y_true, y_preds),
            "precision": precision_score(y_true, y_preds)
        }
    except Exception as e:
        raise CustomException(e)


def train_evaluate_model(models, X_train, y_train, X_valid, y_valid, X_test, y_test, param_grid, cv=3):
    try:
        report = {}
        rows = []  # <-- moved outside the model loop
        best_estimators={}

        for model_name, model in models.items():
            logging.info(f"Starting GridSearchCV for {model_name}")

            with mlflow.start_run(run_name=f"{model_name}_run"):
                gs = GridSearchCV(model, param_grid[model_name], cv=cv, verbose=2, n_jobs=-1)
                gs.fit(X_train, y_train)

                best_model = gs.best_estimator_
                best_model.fit(X_train, y_train)
                best_estimators[model_name]=best_model

                logging.info(f"Best parameters for {model_name}: {gs.best_params_}")

                # predictions
                y_train_pred = best_model.predict(X_train)
                y_valid_pred = best_model.predict(X_valid)
                y_test_pred  = best_model.predict(X_test)

                # compute metrics
                train_score = get_classification_score(y_train, y_train_pred)
                valid_score = get_classification_score(y_valid, y_valid_pred)
                test_score  = get_classification_score(y_test, y_test_pred)

                mlflow.log_params(gs.best_params_)

                for k,v in train_score.items():
                    mlflow.log_metric(f"train_{k}",v)

                for k,v in valid_score.items():
                    mlflow.log_metric(f"valid_{k}",v)

                for k,v in test_score.items():
                    mlflow.log_metric(f"test_{k}",v)

                try:
                    if model_name.lower().startswith('xgboost'):
                     mlflow.xgboost.log_model(best_model,artifact_path=f"{model_name}_model")
                    else:
                        mlflow.sklearn.log_model(best_model,artifact_path=f"{model_name}_model")
                except Exception as e:
                    mlflow.pyfunc.log_model(artifact_path=f"{model_name}_model",python_model=best_model)

                

                # store report
                report[model_name] = {
                    "Train": train_score,
                    "Valid": valid_score,
                    "Test": test_score,
                    "Best_Params": gs.best_params_
                }


            # collect results for dataframe
                for dataset_name, metrics in {"Train": train_score, "Valid": valid_score, "Test": test_score}.items():
                    rows.append({
                        "Model": model_name,
                        "Dataset": dataset_name,
                        "f1": metrics["f1"],
                        "recall": metrics["recall"],
                        "precision": metrics["precision"]
                    })

        # create final results dataframe
        results = pd.DataFrame(rows).sort_values(by=["Dataset", "f1"], ascending=[True, False]).reset_index(drop=True)
        return results,best_estimators

    except Exception as e:
        raise CustomException(e)
