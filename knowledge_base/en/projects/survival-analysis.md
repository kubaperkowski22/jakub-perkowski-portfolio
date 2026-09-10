---
id: project.survival-analysis
language: en
title: Deep Neural Networks in Survival Analysis
source_type: project
source_slug: survival-analysis
source_path: /projekty/survival-analysis
visibility: public
---

# Deep Neural Networks in Survival Analysis

## Project context and objective

This project was developed as part of my master's thesis on applying deep neural networks to survival analysis using oncology data. Survival analysis models the time until a particular event, such as a patient's death, while accounting for censored observations, for which the exact time of the event is unknown.

The main objective was to design, implement, and investigate a mechanism that would make it possible to analyze how DeepSurv and DeepHit operate. I wanted to obtain information about which input features were more strongly weighted by the network and then examine whether adding this mechanism affected predictive performance. Interpretability was the primary motivation; improving evaluation metrics was not the only goal.

The project was research- and implementation-oriented. It did not constitute clinical validation of a diagnostic system or the deployment of a tool for medical decision-making.

## Baseline models

Two deep-learning approaches to survival analysis were compared:

- **DeepSurv** — a neural-network model based on the Cox proportional hazards model. The network learns a nonlinear representation of the input features and produces a scalar risk predictor. Training uses a loss function based on the Cox partial likelihood. The model can be used, among other things, to rank patients by risk and to estimate survival curves.
- **DeepHit** — a discrete-time approach in which time is divided into intervals and the network predicts the probability distribution of an event over time. The implementation used DeepHitSingle, the variant for a single event type. Its loss function combines a likelihood-related component with a ranking component.

The baseline models served as reference points for two custom variants with an attention module. Four architectures were evaluated in total: DeepSurv, DeepHit, AttentionDeepSurv, and AttentionDeepHit.

## Custom modifications

### FeatureAttention module

I implemented a FeatureAttention module in PyTorch and placed it before the main neural network. For a patient's input feature vector, the module computes a vector of weights and uses it to scale the input.

The mechanism consists of three steps:

1. A linear layer transforms the input vector into scores for individual features.
2. A softmax function normalizes the scores into positive weights that sum to 1 for each patient.
3. The original input vector is multiplied element-wise by the calculated weights, and the resulting vector is passed to the subsequent network.

In mathematical notation:

a(x) = softmax(Wx + b)

x_attended = x ⊙ a(x)

The weights depend on the input, so they can differ between patients. Their values indicate how the module relatively weights the features in a given case. A larger weight does not automatically establish that a feature has a causal effect on the prediction.

### AttentionDeepSurv and AttentionDeepHit

The module was integrated with both baseline architectures. After feature scaling, the data passes through a multilayer perceptron (MLP). The DeepSurv variant produces a scalar risk predictor, while the DeepHit variant produces a vector of probabilities for the time intervals.

The custom classes were adapted to the pycox wrappers. AttentionDeepSurv works with CoxPH, and AttentionDeepHit with DeepHitSingle. The discrete-time model used 100 time intervals. The DeepHitSingle configuration used alpha = 0.2 and sigma = 0.1.

I also added a way to retrieve attention weights for input data without tracking gradients, so that they could be analyzed after training and feature rankings could be compared between models.

## Data and preprocessing

### Data sources and characteristics

Seven oncology datasets from the SEER (Surveillance, Epidemiology, and End Results) program, conducted by the National Cancer Institute, were used. The datasets covered different cancer groups, allowing the models to be compared across datasets with different sizes and censoring levels.

| Cancer group | Number of patients | Event rate | Censoring rate |
|---|---:|---:|---:|
| Brain cancer | 65,719 | 80% | 20% |
| Breast cancer | 741,107 | 51% | 49% |
| Leukemia | 145,407 | 69% | 31% |
| Lung cancer | 474,994 | 97% | 3% |
| Lymphoma | 229,218 | 62% | 38% |
| Prostate cancer | 664,874 | 57% | 43% |
| Small intestine cancer | 21,026 | 63% | 37% |

The dataset sizes and percentages come from Table 5.1 of the thesis. Breast cancer was the largest dataset in this comparison, while small intestine cancer was the smallest.

### Feature preparation

The thesis describes preprocessing pipelines adapted to the individual datasets. The main steps included:

- removing records with an undefined survival time (null), defining the time and event-status variables, and removing identifiers that did not carry predictive information;
- standardizing data formats and types, including converting selected textual values into numerical values;
- removing columns with more than 50% missing observations;
- encoding categorical variables using one-hot encoding;
- splitting the data into training (60%), validation (20%), and test (20%) sets, with reproducible splitting using `random_state=42`;
- imputing missing values with the median and standardizing features, with parameters estimated exclusively from the training set.

Separating the data before fitting the imputer and scaler is important because it reduces the risk of information leakage from the test set into training. The detailed interpretability analysis also highlighted that one-hot encoding makes it more difficult to map feature indices directly back to readable clinical names.

## Experimental methodology

### Main experiment

Each of the four models was trained ten times on each of the seven datasets. This corresponds to 280 training runs in the main comparison, excluding additional sensitivity experiments and the case study.

The repetitions were intended to reduce the influence of random weight initialization. The methodology states that the same training, validation, and test split was maintained for each dataset, while individual training runs started from new random weights. Results were aggregated by examining averages, variability, and the best values obtained.

### Training parameters

The main comparison used an MLP with two hidden layers of 32 neurons each, dropout of 0.3, and a learning rate of 0.0001. The batch size was 256. Adam was used for optimization, and L2 regularization was also applied to the attention module.

Early stopping monitored the validation loss with a patience of 10 epochs. This was intended to limit overfitting and reduce training time when the model stopped improving on the validation set.

### Sensitivity experiments

Before the main evaluation, different configurations were compared on three representative datasets: lung cancer, prostate cancer, and small intestine cancer. The experiments included increasing the architecture from (32, 32) to (64, 64) and raising dropout from 0.3 to 0.5.

The results did not indicate a universal benefit from increasing network capacity. Stronger dropout could worsen performance, particularly on the smaller small intestine cancer dataset. The configuration (32, 32), dropout 0.3, and learning rate 0.0001 was selected for the main comparison as a compromise between performance, stability, and computational cost.

## Evaluation

Two main metrics were used:

- **C-index (concordance index)** — measures the model's ability to correctly order comparable observations by risk. A higher value indicates better discrimination.
- **Integrated Brier Score (IBS)** — a time-integrated measure of error in predicted survival probabilities. It reflects the accuracy of probabilistic predictions over time; lower values are preferable.

The metrics answer different questions. A model may rank patients by risk effectively while estimating survival probabilities less accurately. For this reason, both metrics were evaluated rather than basing conclusions solely on the C-index.

The experiments used, among other tools, PyTorch, torchtuples, and pycox for model construction, training, and evaluation, as well as pandas, NumPy, scikit-learn, and lifelines for data processing and auxiliary analyses.

## Main comparison results

The values below come from Tables 6.4–6.10 of the thesis. They represent mean IBS, mean C-index, and the best C-index for each configuration. The best individual result should not be confused with the mean over ten training runs. All values retain the precision reported in the thesis.

| Dataset | Model | Mean IBS ↓ | Mean C-index ↑ | Best C-index ↑ |
|---|---|---:|---:|---:|
| Brain cancer | DeepSurv | 0.0729 | 0.793 | 0.7938 |
| Brain cancer | DeepHit | 0.1539 | 0.7944 | 0.7964 |
| Brain cancer | AttentionDeepSurv | 0.0733 | 0.7935 | 0.7944 |
| Brain cancer | AttentionDeepHit | 0.1464 | 0.7998 | 0.8018 |
| Breast cancer | DeepSurv | 0.1241 | 0.7727 | 0.7732 |
| Breast cancer | DeepHit | 0.1582 | 0.7782 | 0.7796 |
| Breast cancer | AttentionDeepSurv | 0.1247 | 0.773 | 0.7739 |
| Breast cancer | AttentionDeepHit | 0.1563 | 0.7767 | 0.7779 |
| Leukemia | DeepSurv | 0.1172 | 0.7028 | 0.7032 |
| Leukemia | DeepHit | 0.178 | 0.7105 | 0.7112 |
| Leukemia | AttentionDeepSurv | 0.105 | 0.7881 | 0.7891 |
| Leukemia | AttentionDeepHit | 0.17 | 0.7985 | 0.799 |
| Lung cancer | DeepSurv | 0.0319 | 0.7047 | 0.7052 |
| Lung cancer | DeepHit | 0.057 | 0.7078 | 0.7085 |
| Lung cancer | AttentionDeepSurv | 0.0319 | 0.7038 | 0.7046 |
| Lung cancer | AttentionDeepHit | 0.0572 | 0.7062 | 0.7065 |
| Lymphoma | DeepSurv | 0.1231 | 0.7488 | 0.7503 |
| Lymphoma | DeepHit | 0.1739 | 0.7654 | 0.7658 |
| Lymphoma | AttentionDeepSurv | 0.1247 | 0.7473 | 0.7489 |
| Lymphoma | AttentionDeepHit | 0.1751 | 0.7626 | 0.7641 |
| Prostate cancer | DeepSurv | 0.0952 | 0.769 | 0.7693 |
| Prostate cancer | DeepHit | 0.1447 | 0.7695 | 0.7701 |
| Prostate cancer | AttentionDeepSurv | 0.0952 | 0.7692 | 0.7698 |
| Prostate cancer | AttentionDeepHit | 0.1397 | 0.7699 | 0.7705 |
| Small intestine cancer | DeepSurv | 0.1141 | 0.7714 | 0.7752 |
| Small intestine cancer | DeepHit | 0.2084 | 0.7499 | 0.7746 |
| Small intestine cancer | AttentionDeepSurv | 0.1146 | 0.7566 | 0.7823 |
| Small intestine cancer | AttentionDeepHit | 0.1836 | 0.7756 | 0.7845 |

### Interpretation of the results

The largest improvement in C-index was observed for leukemia. The mean C-index of DeepSurv increased from 0.7028 to 0.7881 after adding attention, while DeepHit increased from 0.7105 to 0.7985. At the same time, mean IBS decreased from 0.1172 to 0.105 and from 0.178 to 0.17, respectively.

On the brain cancer dataset, AttentionDeepHit achieved a mean C-index of 0.7998 compared with 0.7944 for baseline DeepHit, with a lower mean IBS (0.1464 versus 0.1539). For prostate cancer, the mean C-index values of all four models fell within the narrow range of 0.769 to 0.7699.

Not all changes were beneficial. On the small intestine cancer dataset, the mean C-index of DeepSurv decreased from 0.7714 to 0.7566 after adding attention, even though the best individual C-index of the attention variant was higher. On some other datasets, changes were small or worsened one of the metrics.

The conclusion is therefore dependent on the data and architecture: the attention mechanism can preserve similar predictive performance and improve it in certain cases, but it does not guarantee an improvement on every dataset. The results do not support a claim that the custom variants are universally better than their baselines.

## Interpretability and attention-weight analysis

After training, rankings of the five highest-weighted features were extracted for each of the seven datasets. Rankings obtained from AttentionDeepSurv and AttentionDeepHit were compared.

### How the rankings were calculated

The notebooks confirm that attention weights were calculated for the test-set patients after training. For a single trained model, the weights were averaged over the patient dimension to obtain one mean feature-weight vector. The features were then sorted by their mean weights. The individual-model visualization displayed the top 15 features.

In the main experiments, each of the ten training runs produced its own mean feature-weight vector. These vectors were then averaged across runs, and the resulting vector was used to generate the final top-15 ranking. The thesis subsequently compared the top-five features from the two attention-based architectures.

Thus, the main-experiment ranking represents an average across both test-set patients and ten training runs. It is not a ranking for one patient, nor is it a ranking derived solely from the single best-performing run.

The weights indicate relative feature weighting by the attention module. They should not be interpreted as a complete measure of each feature's influence on the final prediction, a causal explanation, or a clinical validation of feature importance.

### Comparison of feature rankings

Agreement was very high for some datasets. For lung cancer and prostate cancer, both models identified the same sets of five highest-ranked features, although not always in the same order. In other groups, agreement was partial: the most important features often overlapped, but their order and lower-ranked positions could differ.

The analysis suggested that these differences may be related to the models' different learning objectives: DeepSurv uses a loss associated with the Cox model, whereas DeepHit uses a discrete-time approach with an additional ranking component. Attention weights therefore depend on the learned architecture and optimization objective.

### Limitations of interpretation

The mechanism allows relative feature weighting to be analyzed, but it does not by itself demonstrate that a given parameter causes a medical event. Nor does it provide a complete, model-independent explanation of every prediction.

An important limitation was the use of features after one-hot encoding. The weights refer to input columns that may represent individual categories of clinical variables. Producing a readable medical ranking requires preserving a mapping between the transformed columns and the original variable names and categories.

The thesis also identified the potential for further interpretability verification using other methods and consultation with medical experts. Agreement between rankings should not be presented as clinical confirmation of the importance of particular biomarkers.

## Detailed prostate cancer analysis

The prostate cancer dataset was selected for an additional case study. The thesis justified this choice by its large size, relatively balanced censoring level, and stability of predictive results.

The dataset included 664,874 patients, comprising 380,431 event observations (57.2%) and 284,443 censored observations (42.8%).

With the baseline configuration (32, 32), dropout 0.3, AttentionDeepSurv achieved a mean C-index of 0.7692 and a mean IBS of 0.0952. AttentionDeepHit achieved a mean C-index of 0.7699 and a mean IBS of 0.1397. The results were close to those of the baseline models, and AttentionDeepHit achieved a lower IBS than DeepHit.

The attention-ranking analysis showed agreement between the two variants regarding the set of five highest-ranked input features. The thesis reported their indices after preprocessing but did not provide a complete, unambiguous mapping of those indices back to the original clinical names. For this reason, this document does not assign medical names to them based on assumptions.

## My contribution

As part of the thesis, I implemented the baseline DeepSurv and DeepHit models and developed two custom variants extended with the FeatureAttention mechanism. I integrated them with survival-analysis tools, prepared data-processing pipelines, and conducted comparative experiments on seven oncology datasets.

The project also involved analyzing the effects of network configuration and regularization, evaluating results using C-index and IBS, retrieving and comparing attention weights, and carrying out a detailed prostate cancer case study.

## Conclusions and skills gained

The project gave me experience in implementing and modifying deep-learning architectures, working with censored data, designing experiments, preparing large datasets, and evaluating model quality using metrics appropriate for survival analysis.

The most important conclusion was that adding an interpretability-oriented mechanism does not necessarily cause a substantial deterioration in predictive performance and can lead to improvements in some of the tested configurations. At the same time, effectiveness depends on the characteristics of the data, architecture, and training parameters, so no conclusion should be drawn about the universal superiority of one variant.

The work also demonstrated that obtaining feature weights is only the beginning of the interpretation process. Useful explanations of predictions require, among other things, readable feature mappings, stability analysis, and appropriate validation in the relevant domain.

## Study limitations and future work

The study was based on retrospective oncology data and did not constitute prospective or clinical validation of a system. The results should not be interpreted as evidence of suitability for making treatment decisions.

Further development directions included automating the translation of feature indices after preprocessing into readable medical names, exploring more advanced attention mechanisms, and verifying interpretability with domain experts. Further research could also include a more detailed analysis of result stability and generalization.

## Sources and scope

This document is based on the author's master's thesis excerpt, "Deep Neural Networks in Survival Analysis — Experiments," covering Chapters 5, 6, and 7 (methodology, results, and conclusions), and on information about the author's own contribution confirmed by the author.

Project repository: https://github.com/kubaperkowski22/DL_SurvivalAnalysis

The numerical tables reproduce values from Tables 5.1 and 6.4–6.10 of the thesis. The ranking-aggregation procedure was additionally checked against the supplied DeepSurv and DeepHit attention notebooks. The descriptions of implementation and configuration reflect the methodology documented in the thesis; they do not claim that every item has been independently verified by rerunning the code. This document contains no patient-identifying data or non-public medical information.
