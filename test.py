from trans_util.transcribe_util import start_job, read_dataframe_metadata, validation_file_exist_check, get_job, list_jobs
import boto3
if __name__ == '__main__':
    print('hello')

    client = boto3.client('transcribe')
    job_name = 'testd_pycharm'
    media_uri = 's3://testjhs/data/2202695a8cdc19798ab768d126cdf240.wav'
    media_format = 'wav'
    language_code='ko-KR'

    job = list_jobs('x166e328ecee59683e111a6f3005c6f9e',client )
    print('job : ', job)

    print('come here?')