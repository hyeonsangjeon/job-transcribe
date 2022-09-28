import nlptutti
import nlptutti as nt
from trans_util.transcribe_util import *


groundtruth_hangul_pb =read_txt('tmp_data/groundtruth/1_PB수신고객응대_정답지.txt')
groundtruth_hangul_startup_loans = read_txt('tmp_data/groundtruth/2_은행의신생기업대출안내_정답지.txt')
groundtruth_hangul_insurance = read_txt('tmp_data/groundtruth/3_보험료할증분산정관련문의_정답지.txt')

print("groundtruth_hangul_pb : ", groundtruth_hangul_pb)
print("groundtruth_hangul_startup_loans :", groundtruth_hangul_startup_loans)
print("groundtruth_hangul_insurance : ", groundtruth_hangul_insurance)
print("============================================================================================================\n")

groundtruth_num_pb =read_txt('tmp_data/groundtruth/1_PB 수신고객응대_정답지_숫자로표기.txt')
groundtruth_num_startup_loans = read_txt('tmp_data/groundtruth/2_은행의신생기업대출안내_정답지_숫자로표기.txt')
groundtruth_num_insurance = read_txt('tmp_data/groundtruth/3_보험료할증분산정관련문의_정답지_숫자로표기.txt')

print("groundtruth_num_pb : ", groundtruth_num_pb)
print("groundtruth_num_startup_loans :", groundtruth_num_startup_loans)
print("groundtruth_num_insurance : ", groundtruth_num_insurance)
print("============================================================================================================\n")


aws_pb = read_json('tmp_data/aws/1_PB수신고객응대.json')['results']['transcripts'][0]['transcript']
aws_startup_loans = read_json('tmp_data/aws/2_은행의신생기업대출안내.json')['results']['transcripts'][0]['transcript']
aws_insurance  = read_json('tmp_data/aws/3_보험료할증분산정관련문의.json')['results']['transcripts'][0]['transcript']

print("aws_pb : ", aws_pb)
print("aws_startup_loans :", aws_startup_loans)
print("aws_insurance : ", aws_insurance)
print("============================================================================================================\n")
azure_pb = read_txt('tmp_data/azure/1_PB 수신고객응대.txt')
azure_startup_loans = read_txt('tmp_data/azure/2_은행의신생기업대출안내.txt')
azure_insurance = read_txt('tmp_data/azure/3_보험료할증분산정관련문의.txt')

print("azure_pb : ", azure_pb)
print("azure_startup_loans :", azure_startup_loans)
print("azure_insurance : ", azure_insurance)
print("============================================================================================================\n")

clova_pb = read_json('tmp_data/clova/1_PB수신고객응대.json')['text']
clova_startup_loans = read_json('tmp_data/clova/2_은행의신생기업대출안내.json')['text']
clova_insurance = read_json('tmp_data/clova/3_보험료할증분산정관련문의.json')['text']

print("clova_pb : ", clova_pb)
print("clova_startup_loans :", clova_startup_loans)
print("clova_insurance : ", clova_insurance)
print("============================================================================================================\n")

gcp_pb = read_txt('tmp_data/gcp/1_PB수신고객응대.txt')
gcp_startup_loans = read_txt('tmp_data/gcp/2_은행의신생기업대출안내.txt')
gcp_insurance = read_txt('tmp_data/gcp/3_보험료할증분산정관련문의.txt')

print("gcp_pb : ", gcp_pb)
print("gcp_startup_loans :", gcp_startup_loans)
print("gcp_insurance : ", gcp_insurance)
print("============================================================================================================\n")




init_data_for_hangul = {
    'ground_truth_hangul' : [groundtruth_hangul_pb, groundtruth_hangul_startup_loans, groundtruth_hangul_insurance],
    'ground_truth_number' : [groundtruth_num_pb, groundtruth_num_startup_loans, groundtruth_num_insurance],
    'aws_trans' : [aws_pb, aws_startup_loans, aws_insurance],
    'azure_trans' : [azure_pb, azure_startup_loans, azure_insurance],
    'clova_trains' : [clova_pb, clova_startup_loans, clova_insurance],
    'gcp_trans' : [gcp_pb, gcp_startup_loans, gcp_insurance]

}

init_data_for_num = {
    'ground_truth_number' : [groundtruth_num_pb, groundtruth_num_startup_loans, groundtruth_num_insurance],
    'aws_trans' : [aws_pb, aws_startup_loans, aws_insurance],
    'azure_trans' : [azure_pb, azure_startup_loans, azure_insurance],
    'clova_trains' : [clova_pb, clova_startup_loans, clova_insurance],
    'gcp_trans' : [gcp_pb, gcp_startup_loans, gcp_insurance]

}

cs_df_hangul = pd.DataFrame(init_data_for_hangul)
cs_df_hangul.to_csv('./preprocess/cs_hangul_data.csv')

cs_df_num = pd.DataFrame(init_data_for_hangul)
cs_df_num.to_csv('./preprocess/cs_num_data.csv')

print(cs_df_hangul)

