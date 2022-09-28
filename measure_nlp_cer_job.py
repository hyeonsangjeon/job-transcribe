import nlptutti as nt
from trans_util.transcribe_util import start_job, read_dataframe_metadata, get_transcribe_sentence, api_error_log
import boto3
from botocore.exceptions import ClientError
import requests

if __name__ == '__main__':
    test_sentence = '안녕하세요 나는 전현상입니다.'
    valid_sentence = '안녕하세요나는전현상입니다.'
    res = nt.get_cer(test_sentence,valid_sentence)
    print("result : ", res)

    #1. df로 메타데이터 3922를 가져온다.
    bucket_name = 'stthsjeon'
    prefix_name = 'input/beautiful-voice/0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b/'
    meta_df = read_dataframe_metadata('stthsjeon', 'input/beautiful-voice/',
                                      '0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b-metadata.txt')
    print('meta_df : ', meta_df)
    client = boto3.client('transcribe')

    for i in meta_df.index:
        file_name = meta_df._get_value(i,'file_name')
        job_name = file_name.rstrip('.wav')
        try:
            transcribe_sentence = get_transcribe_sentence(job_name, client)
        except ClientError:
            transcribe_sentence = 'ER01'
            api_error_log('faild_id : ' + job_name)

        if transcribe_sentence !='ER01':
            ground_truth_sentence = meta_df._get_value(i,'ground_truth')
            cer = nt.get_cer(ground_truth_sentence, transcribe_sentence)['cer']
            print('ground_truth_sentence : ', ground_truth_sentence)
            print('transcribe_sentence : ', transcribe_sentence)
            print('cer : ', cer)
            print('\n ')
            meta_df._set_value(i,'transcribe_sentence', transcribe_sentence)
            meta_df._set_value(i, 'cer', cer)


    meta_df.to_csv('./result.csv')






#    print(" simple : ", job_simple)
