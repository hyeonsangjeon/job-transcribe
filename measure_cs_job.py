import nlptutti as nt
from trans_util.transcribe_util import *
import boto3
from botocore.exceptions import ClientError
import requests
import pandas as pd

if __name__ == '__main__':
    df_hangul = pd.read_csv('./preprocess/cs_hangul_data.csv')
    df_num = pd.read_csv('./preprocess/cs_num_data.csv')



df_hangul['cer_aws'] = df_hangul.apply(lambda row : nt.get_cer(row['ground_truth_hangul'], row['aws_trans'])['cer'],  axis = 1)
df_hangul['cer_azure'] = df_hangul.apply(lambda row : nt.get_cer(row['ground_truth_hangul'], row['azure_trans'])['cer'],  axis = 1)
df_hangul['cer_clova'] = df_hangul.apply(lambda row : nt.get_cer(row['ground_truth_hangul'], row['clova_trains'])['cer'],  axis = 1)
df_hangul['cer_gcp'] = df_hangul.apply(lambda row : nt.get_cer(row['ground_truth_hangul'], row['gcp_trans'])['cer'],  axis = 1)
df_hangul.to_csv('./result/cs_hangul_result.csv')
print("GroundTruth is hangul. Process success.")


df_num['cer_aws'] = df_num.apply(lambda row : nt.get_cer(row['ground_truth_number'], row['aws_trans'])['cer'],  axis = 1)
df_num['cer_azure'] = df_num.apply(lambda row : nt.get_cer(row['ground_truth_number'], row['azure_trans'])['cer'],  axis = 1)
df_num['cer_clova'] = df_num.apply(lambda row : nt.get_cer(row['ground_truth_number'], row['clova_trains'])['cer'],  axis = 1)
df_num['cer_gcp'] = df_num.apply(lambda row : nt.get_cer(row['ground_truth_number'], row['gcp_trans'])['cer'],  axis = 1)

df_num.to_csv('./result/cs_number_result.csv')
print("GroundTruth is number. Process successed.")