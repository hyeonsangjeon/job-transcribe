from trans_util.transcribe_util import start_job, read_dataframe_metadata, validation_file_exist_check, get_job, list_jobs, delete_job
import boto3
if __name__ == '__main__':
    client = boto3.client('transcribe')
    bucket_name = 'stthsjeon'
    prefix_name = 'input/beautiful-voice/0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b/'
    meta_df = read_dataframe_metadata('stthsjeon', 'input/beautiful-voice/',
                                      '0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b-metadata.txt')
    print("mets_df : ", meta_df)
    tmp = 0
    for i in meta_df.index:
        file_name = meta_df._get_value(i,'file_name')
        job_name = file_name.rstrip('.wav') # df.로 루프를 돌리는데, 잡아름은 meta의 파일명이다.
        tmp = tmp + 1
        delete_job(job_name, client)
        print("Count ", tmp, "JOB processed : ", job_name)
