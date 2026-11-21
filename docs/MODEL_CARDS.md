# Core model cards

## Intended use

Educational NBA exploration and presentation. Models estimate outcomes, not causal player quality or guaranteed betting returns. They contain no verified injuries, active lineups, guarding assignments or tracking data.

Inputs come from [Eoin A Moore's NBA box-score dataset](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores). [Historical odds](https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024) are retrospective comparisons only; their timing is unknown and they are excluded from core model features. `startingPosition` presence is retained as a source proxy, not assumed to be uniformly complete; starter-share features are omitted from the core models pending validation of that field.

## Chronology and persistence

With latest completed season 2025-26, train through 2022-23, validate 2023-24, reserve 2024-25 for residual/calibration diagnostics, and test 2025-26. Preprocessors fit training rows only. Linear and small histogram-tree candidates are selected using validation log loss (classification) or MAE (regression). No retuning uses the test set. Current 2026-27 outcomes do not train these models. Exact counts, selected models, cutoff and performance are saved in `app_data/evaluation.json`.

Artifacts persist model, preprocessing, exact feature order, calibration-period residuals, training cutoff, prediction-availability cutoff, data version and actual backtests. Never load untrusted pickle files. Rebuilding data requires rebuilding models. Historical inference predating validation/calibration availability is rejected; saved out-of-sample backtests are the supported historical view.

## Team model

Home win: historical home-rate and chronological Elo baselines, logistic and histogram-gradient-boosting candidates. Margin and total: ridge and histogram-gradient-boosting candidates. Inputs include lagged 5/10/20 and season features, differences and sums, rest and pregame Elo. Positive margin favors home. Model expected scores follow `(total +/- margin)/2`; a winner/margin disagreement is shown rather than silently repaired.

80% margin prediction intervals and cover probabilities use separate calibration-season residuals, mapped to non-tied integer final margins. This empirical error-distribution assumption may drift. Integer spreads may push; half-point lines cannot. A prediction interval is not a confidence interval for mean prediction.

## Player model

Targets: points, rebounds, assists. Baseline: prior 10 played-game average, with available-history fallback. Candidate regressors use prior player production/minutes, home/rest and opponent prior defensive rating/pace. Predictions are player-versus-team. Opposing-player logs supply descriptive encounter context; no defender-specific causal effect is trained. Quantities are conditional on appearing, not availability-adjusted expectations.

Approximate 80% intervals use calibration residuals; low count estimates are clipped at zero. Clipping and non-integer expected counts are explicit presentation conventions. Sparse history uses training-fitted imputation and broad context; no invented physical archetypes.

## Breakout model

Label: next-season MPG >=20, MPG increase >=5 and eligible PRA-per-36 percentile increase >=15. Candidates have base-season GP >=20, MPG >=15 and PRA percentile <80. Historical labels require sufficient observed future games; absent next-season rows are excluded, causing survivorship bias. Prospective selection never requires future outcomes. Rookies lack a base season and are excluded.

Standardized class-weighted logistic regression is evaluated alongside a small tree candidate. Tree selection requires better validation probability loss. Feature values come from the base season or earlier; outcome season defines split membership. Coefficients, when the linear model is selected, explain signed log-odds contributions. Tree outputs are explicitly not accompanied by fabricated local explanations. The tracker is descriptive and does not retroactively change preseason forecasts.

The evaluation currently reserves one final test season and a separate calibration season rather than claiming two untouched final tests. Report actual precision@15, PR-AUC, base rates and calibration; do not manufacture a baseline-beating result. No separate probability-calibration mapping is fitted: the displayed buckets measure calibration rather than guaranteeing it. Detailed metrics and baseline comparisons are generated into the implementation report. Tree explanations measure the change in model probability when one feature is reset to its training median; they are model sensitivities, not additive SHAP values or causal effects.

## Deferred and unavailable

Neural models, SHAP, BPM/VORP, causal defensive assignments, shot-location/quarter player data, authoritative advanced season aggregations and dated roster/injury adjustments are not implemented. Six advanced season slots show N/A rather than misleading game-level means. Live odds are optional; API error/cache tests use mocks and do not establish live account access.
