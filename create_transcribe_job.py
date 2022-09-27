import logging
from trans_util.transcribe_util import start_job, read_dataframe_metadata, validation_file_exist_check
import boto3
import pandas as pd
if __name__ == '__main__':
    print('hello')

    client = boto3.client('transcribe')
    job_name = 'testd_pycharm'
    #media_uri = 's3://testjhs/data/2202695a8cdc19798ab768d126cdf240.wav'
    media_format = 'wav'
    language_code='ko-KR'
    #start_job(job_name, media_uri, media_format, language_code, client)




    #1. df로 메타데이터 3922를 가져온다.
    bucket_name = 'stthsjeon'
    prefix_name = 'input/beautiful-voice/0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b/'
    meta_df = read_dataframe_metadata('stthsjeon', 'input/beautiful-voice/',
                                      '0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b-metadata.txt')
    print("mets_df : ", meta_df)


    media_prefix_uri ='s3://stthsjeon/input/beautiful-voice/0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b/'

    fault_cnt = 0
    tmp = 0
    for i in meta_df.index:
        file_name = meta_df._get_value(i,'file_name')
        job_name = file_name.rstrip('.wav') # df.로 루프를 돌리는데, 잡아름은 meta의 파일명이다.
        s3_row_uri = media_prefix_uri + file_name

        #print("check : ",s3_row_uri)
        #print("file : ", file_name,"    |    job : ", job_name, "         |         s3_url : ", s3_row_uri )

        if validation_file_exist_check(bucket_name, prefix_name,file_name) == True:
            tmp = tmp + 1
            start_job(job_name, s3_row_uri, media_format, language_code, client)
            print("Count ", tmp , "JOB processed : ", job_name)
        else:
            fault_cnt = fault_cnt +1


    print("Final fault_cnt : ", fault_cnt)


    #2. df로 media_url 변수를 만든다.
    ## 루프 안에서 3922개 잡을 돌린다.

    print("TEST : ", validation_file_exist_check(bucket_name, prefix_name, '2202695a8cdc19798ab768d126cdf240.wav'))