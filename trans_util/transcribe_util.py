import logging
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import io
import requests

logger = logging.getLogger(__name__)
def start_job(job_name, media_uri, media_format, language_code, transcribe_client,vocabulary_name=None):
    """
    Starts a transcription job. This function returns as soon as the job is started.
    To get the current status of the job, call get_transcription_job. The job is
    successfully completed when the job status is 'COMPLETED'.

    :param job_name: The name of the transcription job. This must be unique for
                     your AWS account.
    :param media_uri: The URI where the audio file is stored. This is typically
                      in an Amazon S3 bucket.
    :param media_format: The format of the audio file. For example, mp3 or wav.
    :param language_code: The language code of the audio file.
                          For example, en-US or ja-JP
    :param transcribe_client: The Boto3 Transcribe client.
    :param vocabulary_name: The name of a custom vocabulary to use when transcribing
                            the audio file.
    :return: Data about the job.
    """

    try:
        job_args = {
            'TranscriptionJobName': job_name,
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code}
        if vocabulary_name is not None:
            job_args['Settings'] = {'VocabularyName': vocabulary_name}
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logger.info("Started transcription job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't start transcription job %s.", job_name)
        raise
    else:
        return job


def read_dataframe_metadata(bucket_name, prefix_name, file):
    client = boto3.client('s3')
    prefix = prefix_name
    paginator = client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=bucket_name,
        Prefix=prefix
    )

    for page in response_iterator:
        for content in page['Contents']:
            name = content['Key'].split('/')[-1]
            result =''
            if name == file:
                # print(content)
                key = content['Key']
                # print('key: ', key)
                # print('Bucket :', bucket_name)
                obj = client.get_object(Bucket=bucket_name, Key=key)
                result = pd.read_csv(io.BytesIO(obj["Body"].read()), sep='|', names = ['file_name', 'ground_truth', 'word_lenth'], header=0)
                return result
                break

    return result


def validation_file_exist_check(bucket_name, prefix_name, file): # 수정필요
    result = False

    client = boto3.client('s3')
    prefix = prefix_name
    paginator = client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=bucket_name,
        Prefix=prefix
    )

    for page in response_iterator:
        for content in page['Contents']:
            name = content['Key'].split('/')[-1]
            if name == file:
                result = True
    return result


# snippet-start:[python.example_code.transcribe.GetTranscriptionJob]
def get_job(job_name, transcribe_client):
    """
    Gets details about a transcription job.
    :param job_name: The name of the job to retrieve.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The retrieved transcription job.
    """

    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        logger.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logger.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job
# snippet-end:[python.example_code.transcribe.GetTranscriptionJob]


# snippet-start:[python.example_code.transcribe.ListTranscriptionJobs]
def list_jobs(job_filter, transcribe_client):
    """
    Lists summaries of the transcription jobs for the current AWS account.
    :param job_filter: The list of returned jobs must contain this string in their
                       names.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The list of retrieved transcription job summaries.
    """
    try:
        response = transcribe_client.list_transcription_jobs(
            JobNameContains=job_filter)
        jobs = response['TranscriptionJobSummaries']
        next_token = response.get('NextToken')
        while next_token is not None:
            response = transcribe_client.list_transcription_jobs(
                JobNameContains=job_filter, NextToken=next_token)
            jobs += response['TranscriptionJobSummaries']
            next_token = response.get('NextToken')
        logger.info("Got %s jobs with filter %s.", len(jobs), job_filter)
    except ClientError:
        logger.exception("Couldn't get jobs with filter %s.", job_filter)
        raise
    else:
        return jobs
# snippet-end:[python.example_code.transcribe.ListTranscriptionJobs]

# snippet-start:[python.example_code.transcribe.DeleteTranscriptionJob]
def delete_job(job_name, transcribe_client):
    """
    Deletes a transcription job. This also deletes the transcript associated with
    the job.
    :param job_name: The name of the job to delete.
    :param transcribe_client: The Boto3 Transcribe client.
    """
    try:
        transcribe_client.delete_transcription_job(
            TranscriptionJobName=job_name)
        logger.info("Deleted job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't delete job %s.", job_name)
        raise
# snippet-end:[python.example_code.transcribe.DeleteTranscriptionJob]


def get_transcribe_sentence(job_name, transcribe_client):
    job_simple = get_job(job_name, transcribe_client)
    transcript_simple = requests.get(job_simple['Transcript']['TranscriptFileUri']).json()
    full_sentence =  transcript_simple['results']['transcripts'][0]['transcript']
    return full_sentence



def api_error_log(message):
    with open('./api_error.log', 'a') as f:
        f.write(message)
        f.write('\n')


def read_txt(filename):
    with open(filename, 'r') as f:
        txt = f.read()
    return txt