---
id: project.news-extractor
language: en
title: News Extractor
source_type: project
source_slug: news-extractor
source_path: /projekty/news-extractor
visibility: public
---

# News Extractor

## Project context and objective

News Extractor is an academic project that I developed independently for a Natural Language Processing course. The project focused on processing Polish texts, news classification, and information extraction from textual content.

The goal was to gain practical experience with classical NLP and machine-learning methods and compare several classification algorithms on the same test dataset. The project is smaller in scope than my degree projects and AI Portfolio Assistant, but it demonstrates experience in text-data preparation, model training, and result analysis.

## Data and text preparation

I prepared the training data myself. The dataset was used to train and compare models classifying Polish texts.

The project used Polish-language processing tools, including spaCy, and TF-IDF text representation. TF-IDF transforms documents into numerical feature vectors based on word occurrence and their importance across the corpus. These vectors can then be used as input to classical classifiers.

I do not currently have a confirmed full dataset specification, the number of classes, the exact training and validation split, or all preprocessing steps. I therefore do not attribute unverified procedures or dataset sizes to the project. Data prepared with the help of a generative model is also not equivalent to independently collected and manually labeled real-world data.

## Classification models

I compared three classical machine-learning algorithms:

- **Support Vector Machine (SVM)** — a classifier that learns a decision boundary between classes from vector representations of text.
- **Naive Bayes** — a probabilistic classifier based on Bayes' theorem and a conditional-independence assumption between features.
- **Random Forest** — an ensemble model combining multiple decision trees.

The models were used to compare classification performance. This was not a project involving the training of an LLM or the fine-tuning of a transformer.

## Information extraction

The project also included an information-extraction component. I used spaCy for Polish-language analysis, including working with tokens and linguistic structure.

The exact role of the individual extraction components, rules, and representations requires further verification in the code. I do not currently claim specific extraction-quality results or treat information extraction as equivalent to news classification.

## Classification evaluation

I evaluated the results using confusion matrices created for each model. On a test dataset containing 302 records, I obtained the following numbers of incorrect classifications:

| Model | Incorrect classifications | Correct classifications | Accuracy |
|---|---:|---:|---:|
| SVM | 29 | 273 | 90.40% |
| Naive Bayes | 24 | 278 | 92.05% |
| Random Forest | 46 | 256 | 84.77% |

Accuracy was calculated as the number of correct classifications divided by 302. In this particular comparison, Naive Bayes made the fewest errors, followed by SVM, while Random Forest made the most.

These results refer to one reported test dataset. They do not prove that Naive Bayes is universally the best model for text classification. I do not currently have confirmed precision, recall, F1-score, confidence intervals, or repeated experiments with different data splits, so I do not report such values.

## My contribution and skills gained

I independently developed the academic project, prepared training data, applied classical classification models, and compared their results using confusion matrices.

The project helped me practice the fundamentals of NLP, text representation, supervised classification, and model-result interpretation. It complements my more extensive deep-learning and application-development projects.

## Limitations and future work

The main limitations are the project's small academic scope and the use of small amount of data. I have not currently performed additional verification of label quality, data representativeness, or model robustness on texts from other sources.

A possible extension would be to reproduce the full pipeline, document the classes and data provenance, conduct additional validation, and compare the results with modern text representations. These are potential future improvements, not features I present as already completed.

## Sources and document scope

Project repository: https://github.com/kubaperkowski22/News-extractor---NLP

The description of the project's independent development and the error counts for the individual models is based on information confirmed by me. This document is a short portfolio description rather than complete experimental documentation. Implementation details that I do not currently remember or that have not been reverified are not presented as confirmed facts.
