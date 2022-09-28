from trans_util.transcribe_util import start_job, read_dataframe_metadata, validation_file_exist_check, get_job, list_jobs
import boto3
import requests
if __name__ == '__main__':
    print('hello')

    client = boto3.client('transcribe')
    job_name = 'testd_pycharm'
    media_uri = 's3://testjhs/data/2202695a8cdc19798ab768d126cdf240.wav'
    media_format = 'wav'
    language_code='ko-KR'

    #job = list_jobs('x166e328ecee59683e111a6f3005c6f9e',client )
    #print('job : ', job)

    job_simple = get_job('3595d05e5f1031ae21b078e91df0363f', client)
    print('come here?', job_simple)

    transcript_simple = requests.get(job_simple['Transcript']['TranscriptFileUri']).json()

    print(" simple : ", transcript_simple['results']['transcripts'][0]['transcript'])