"""Chronological models and artifact validation; trusted local files only."""
from datetime import datetime, timezone
import json
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, log_loss, brier_score_loss, roc_auc_score, average_precision_score
from src.pipeline import ROOT, APP, PROCESSED

ARTIFACTS=ROOT/"artifacts"


def estimator(classifier=False, nonlinear=False):
    model=(HistGradientBoostingClassifier(max_iter=60, max_leaf_nodes=15, random_state=42) if classifier else
           HistGradientBoostingRegressor(max_iter=60, max_leaf_nodes=15, random_state=42)) if nonlinear else (
           LogisticRegression(max_iter=1500,random_state=42) if classifier else Ridge(alpha=10))
    return make_pipeline(SimpleImputer(strategy="median",keep_empty_features=True),StandardScaler(),model)


def metrics(y,p,classification=False):
    if classification:
        clipped=np.clip(p,1e-6,1-1e-6)
        return dict(log_loss=float(log_loss(y,clipped,labels=[0,1])),brier=float(brier_score_loss(y,p)),
                    accuracy=float(np.mean((p>=.5)==y)),
                    roc_auc=float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
                    pr_auc=float(average_precision_score(y,p)) if np.sum(y)>0 else None)
    return dict(mae=float(mean_absolute_error(y,p)),rmse=float(np.sqrt(mean_squared_error(y,p))),bias=float(np.mean(p-y)))


def save(name, payload):
    import platform
    import sklearn
    ARTIFACTS.mkdir(exist_ok=True)
    payload["created_at"]=datetime.now(timezone.utc).isoformat()
    payload["dataset_version"]=json.loads((APP/"manifest.json").read_text())["version"]
    payload["packages"]={"python":platform.python_version(),"scikit-learn":sklearn.__version__,"pandas":pd.__version__,"numpy":np.__version__}
    with (ARTIFACTS/f"{name}.pkl").open("wb") as stream: pickle.dump(payload,stream)


def load(name):
    path=ARTIFACTS/f"{name}.pkl"
    if not path.exists(): raise ValueError("Models are not prepared. Run scripts/train_models.py first.")
    with path.open("rb") as stream: payload=pickle.load(stream)
    version=json.loads((APP/"manifest.json").read_text())["version"]
    if version!=payload["dataset_version"]: raise ValueError("Model/data version mismatch; rebuild models.")
    return payload


def fit_task(frame,features,target,classification=False,weights=False):
    """Recent completed seasons: validation, calibration, final test; never mix games."""
    latest=int(json.loads((APP/"manifest.json").read_text())["latest_completed_start"])
    train=frame[frame.season_start<=latest-3]
    val=frame[frame.season_start==latest-2]
    cal=frame[frame.season_start==latest-1]
    test=frame[frame.season_start==latest]
    if any(part.empty for part in [train,val,cal,test]): raise ValueError("Insufficient completed seasons for chronological evaluation")
    models={"linear":estimator(classification),"tree":estimator(classification,True)}
    if weights and classification: models["linear"][-1].set_params(class_weight="balanced")
    results=[]
    for name,model in models.items():
        model.fit(train[features],train[target])
        pred=model.predict_proba(val[features])[:,1] if classification else model.predict(val[features])
        results.append(dict(model=name,period="validation",n=len(val),**metrics(val[target].to_numpy(),pred,classification)))
    criterion="log_loss" if classification else "mae"
    chosen=min(results,key=lambda r:r[criterion])["model"]
    model=models[chosen]  # No refit on the untouched test period.
    predictions=[]
    for label,part in [("calibration",cal),("test",test)]:
        pred=model.predict_proba(part[features])[:,1] if classification else model.predict(part[features])
        results.append(dict(model=chosen,period=label,n=len(part),**metrics(part[target].to_numpy(),pred,classification)))
        row=part[[c for c in ["game_id","player_id","season","season_start"] if c in part]].copy()
        row["actual"]=part[target].values; row["prediction"]=pred; row["period"]=label
        predictions.append(row)
    cp=predictions[0]
    test_predictions=predictions[1]
    if classification:
        calibration=[]
        buckets=pd.cut(test_predictions.prediction,[0,.2,.4,.6,.8,1],include_lowest=True)
        for bucket,g in test_predictions.groupby(buckets,observed=True):
            calibration.append(dict(bucket=str(bucket),n=len(g),predicted=float(g.prediction.mean()),actual=float(g.actual.mean())))
    else:
        errors=cp.actual-cp.prediction
        low,high=np.quantile(errors,[.1,.9])
        calibration={"prediction_interval_80_coverage":float(((test_predictions.actual>=test_predictions.prediction+low)&(test_predictions.actual<=test_predictions.prediction+high)).mean())}
    return dict(model=model,features=features,selected=chosen,results=results,
                calibration=calibration,
                inference_available_after=str(cal.date.max()) if "date" in cal else f"{latest}-07-01",
                split_counts={"train":len(train),"validation":len(val),"calibration":len(cal),"test":len(test)},
                residuals=(cp.actual-cp.prediction).to_numpy(),training_cutoff=str(train.date.max()) if "date" in train else f"{latest-2}-07-01",
                predictions=pd.concat(predictions,ignore_index=True))


def cover_distribution(predicted_margin, residuals, spread):
    """Empirical held-out errors mapped to non-tied integer NBA margins."""
    margins=np.rint(predicted_margin+np.asarray(residuals))
    zeros=margins==0
    margins[zeros]=np.where((predicted_margin+np.asarray(residuals))[zeros]>=0,1,-1)
    adjusted=margins+spread
    return dict(home_cover=float(np.mean(adjusted>0)),away_cover=float(np.mean(adjusted<0)),
                push=float(np.mean(adjusted==0)),low=float(np.quantile(margins,.1)),high=float(np.quantile(margins,.9)))
