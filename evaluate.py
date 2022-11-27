# Aadit S Mehrotra
# 20756049


import argparse
import csv
import os.path
import re

import pandas as pd
from parsers import QrelsParser, ResultsParser
from scipy import stats
from measures import Measures

def parse_args():
    parser = argparse.ArgumentParser(description='Program that calculates Average Precision, Precision@10, NDCG@10, '
                                                 'NDCG@1000 and Time-Based Gain for a given topic results file and '
                                                 'Qrels file')
    parser.add_argument('--qrel', required=True)
    parser.add_argument('--output_directory', required=True)
    parser.add_argument('--results', required=False)
    parser.add_argument('--results_files', required=False, nargs='*')
    parser.add_argument('--compare', required=False,nargs=2)
    args = parser.parse_args()
    return args.qrel, args.output_directory, args.results, args.results_files, args.compare


def measures_to_csv(name, measures, output_location):
    if not os.path.exists(output_location):
        os.makedirs(output_location[::-1])
    with open(output_location + '{}.csv'.format(name), 'w') as csvfile:
        fieldnames = ['measure', 'query_id', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for measure_key, measure in measures.measures_dict.items():
            for key, value in measure.items():
                writer.writerow({'measure': measure_key, 'query_id': key, 'score': value})


def append_to_average_file(csv_name, name, measures):
    with open(csv_name, 'a') as csvfile:
        fieldnames = ['Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        mean_ap = float(sum(measures.average_precision.values())) / len(measures.average_precision.values())
        mean_p_10 = float(sum(measures.precision_at_10.values())) / len(measures.precision_at_10.values())
        mean_ndcg_10 = float(sum(measures.ndcg_10.values())) / len(measures.ndcg_10.values())
        mean_ndcg_1000 =float(sum(measures.ndcg_1000.values())) / len(measures.ndcg_1000.values())
        mean_tbg = float(sum(measures.time_based_gain.values())) / len(measures.time_based_gain.values())
        writer.writerow({'Run Name': name,
                         'Mean Average Precision': '{:.3f}'.format(mean_ap),
                         'Mean P@10': '{:.3f}'.format(mean_p_10),
                         'Mean NDCG@10': '{:.3f}'.format(mean_ndcg_10),
                         'Mean NDCG@1000': '{:.3f}'.format(mean_ndcg_1000),
                         'Mean TBG': '{:.3f}'.format(mean_tbg)})

def bad_format_run(name, output_location):
    with open(output_location + 'hw3-5a-asmehrot.csv', 'a') as csvfile:
        fieldnames = ['Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'Run Name': name,
                         'Mean Average Precision': 'bad format',
                         'Mean P@10': 'bad format',
                         'Mean NDCG@10': 'bad format',
                         'Mean NDCG@1000': 'bad format',
                         'Mean TBG': 'bad format'})


def calculate_summary_statistics(output_location):

    average_csv = 'measures_average.csv'
    measures = ['Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
    measures_dict = {'Mean Average Precision': 'average_precision',
                     'Mean P@10': 'precision_at_10',
                     'Mean NDCG@10': 'ndcg_10',
                     'Mean NDCG@1000': 'ndcg_1000',
                     'Mean TBG': 'time_based_gain'}

    if not os.path.exists(output_location):
        print("Results don't exist")
        return

    with open(output_location + 'statistics.csv', 'w') as csvfile:
        fieldnames = ['Effectiveness Measure', 'Best Run Score', 'Second Best Run Score', 'Relative Percent Improvement',
                      'Two-sided Paired t-Test p-value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        df = pd.read_csv(output_location + average_csv)
        if "bad format" in df["Mean Average Precision"]:
            df = df.drop(df[df["Mean Average Precision"] == "bad format"].index)

        for measure in measures:
            # Convert the value columns to floats to allow numeric handling
            df[measure] = df[measure].replace('bad format', 0).astype(float)
            max_score = df[measure].max(axis=0)

            # Retrieve highest scoring student run
            max_score_row = df[df[measure] == max_score]
            max_score_row_name = max_score_row["Run Name"].item()

            # Retrieve second highest scoring student run
            temp = df.drop(df[df["Run Name"] == max_score_row_name].index)
            if not temp.empty:
                max_score_2 = temp[measure].max(axis=0)
                max_score_2_row = temp[temp[measure] == max_score_2]
                max_score_2_name = max_score_2_row["Run Name"].item()

                max_scores = get_raw_scores(output_location, max_score_row_name, measures_dict[measure])
                max_2_scores = get_raw_scores(output_location, max_score_2_name, measures_dict[measure])

                if len(max_scores) == len(max_2_scores):
                    p_value = stats.ttest_rel(max_scores, max_2_scores)[1]
                else:
                    max_scores_avg = [sum(max_scores) / len(max_scores), sum(max_scores) / len(max_scores)]
                    max_2_scores_avg = [sum(max_2_scores) / len(max_2_scores), sum(max_2_scores) / len(max_2_scores)]
                    p_value = stats.ttest_rel(max_scores_avg, max_2_scores_avg)[1]

                impr = (max_score / max_score_2 - 1)*100

                print("Summary ---- {}".format(measure))
                writer.writerow({'Effectiveness Measure': measure,
                                 'Best Run Score': '{:.3f}'.format(max_score),
                                 'Second Best Run Score': '{:.3f}'.format(max_score_2),
                                 'Relative Percent Improvement': '{:.3f}%'.format(impr),
                                 'Two-sided Paired t-Test p-value': p_value})
            else:
                print("Summary ---- {}".format(measure))
                print("Only a single row, possibly due to bad format")
                writer.writerow({'Effectiveness Measure': measure,
                                 'Best Run Score': '{:.3f}'.format(max_score),
                                 'Second Best Run Score': 'N/A',
                                 'Relative Percent Improvement': 'N/A',
                                 'Two-sided Paired t-Test p-value': 'N/A'})


def get_raw_scores(results_dir_path, name, measure):
    filepath = results_dir_path + name + ".csv"
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        measures = df[df['measure'] == measure]['score']
        return measures.tolist()
    else:
        print("Results file doesn't exist for {}".format(name))


def calculate_measures(qrel, results_files, results_dir_path, output_location):
    if not os.path.exists(output_location):
        os.makedirs(output_location[:-1])
    csv_name = output_location + 'measures_average.csv'
    with open(csv_name, 'w') as csvfile:
        fieldnames = ['Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for result in results_files:
        name = result.split(".")[0]
        print("Measures for: {}".format(name))
        try:
            results = ResultsParser(results_dir_path + result).parse()
            measures = Measures(qrel, results[0], results[1], result)
            measures_to_csv(name, measures, output_location)
            append_to_average_file(csv_name, name, measures)
        except (ResultsParser.ResultsParseError, ValueError, FileNotFoundError) as e:
            print("Not Able to print: {}, bad format".format(name))
            bad_format_run(name, output_location)
            continue


def calculate_measures_for_particular_resultsFiles(qrel, results_files, output_location):
    if not os.path.exists(output_location):
        os.makedirs(output_location[:-1])
    csv_name = output_location + 'measures_average.csv'
    with open(csv_name, 'w') as csvfile:
        fieldnames = ['Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    for r in results_files:
        filename = r.split("/")
        filename = filename[len(filename) - 1]
        name = filename.split(".")[0]
        print("Measures for: {}".format(name))
        try:
            results = ResultsParser(r).parse()
            measures = Measures(qrel, results[0], results[1], r)
            measures_to_csv(name, measures, output_location)
            append_to_average_file(csv_name, name, measures)
        except (ResultsParser.ResultsParseError, ValueError, FileNotFoundError) as e:
            print("Not Able to print: {}, bad format".format(name))
            bad_format_run(name, output_location)
            continue


def compare_results(output_1, output_2, output_location):
    if not os.path.exists(output_location):
        os.makedirs(output_location[:-1])
    df_1 = pd.read_csv(output_1)
    df_2 = pd.read_csv(output_2)
    new_df = pd.merge(df_1, df_2, how='left', left_on=['measure', 'query_id'], right_on=['measure', 'query_id'])
    new_df = new_df.drop(new_df[new_df["score_x"] >= new_df["score_y"]].index)
    new_df.sort_values(by=['query_id'], inplace=True)
    csv_name = output_location + 'compare.csv'
    new_df.to_csv(csv_name, index=False)


qrelPath, output_loc, results_dirPath, resultsFiles, compare = parse_args()
qrel = QrelsParser(qrelPath).parse()
# print(qrel, output_location, results_dir_path, results_files)

if results_dirPath is not None:
    results_dirFiles = os.listdir(results_dirPath)
    calculate_measures(qrel, results_dirFiles, results_dirPath, output_loc)
    calculate_summary_statistics(output_loc)
elif resultsFiles is not None:
    calculate_measures_for_particular_resultsFiles(qrel, resultsFiles, output_loc)
    calculate_summary_statistics(output_loc)
    if compare is not None:
        compare_results(compare[0], compare[1], output_loc)