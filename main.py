# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import boto3
import pandas as pd
import io

from trans_util.transcribe_util import read_dataframe_metadata


if __name__ == '__main__':
    df = read_dataframe_metadata('stthsjeon', 'input/beautiful-voice/', '0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b-metadata.txt')
    #df = search_s3('testjhs', 'data/', '0c7fd07d-2b8b-0d7c-2cbd-09a6c9c6161b-metadata.txt')
    new_data = ['2202695a8cdc19798ab768d126cdf240.wav','경영계획 수립 시 연간 판매계획을 근거하여 기초재고 및 재고계획을 반영한 연간 생산계획을 수립하는 과정이 필요합니다.',65]
    df.loc[len(df)] = new_data

    print('df', df)
    df.to_csv('./meta_voice_data_3922.csv')



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
