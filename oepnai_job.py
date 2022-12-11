import whisper
import pandas as pd
import os
import nlptutti as nt
import time
import datetime

#model = whisper.load_model("medium", device="cpu")
model = whisper.load_model("medium", device="cuda")
model.encoder.to("cuda:0")
model.decoder.to("cuda:1")
model.decoder.register_forward_pre_hook(lambda _, inputs: tuple([inputs[0].to("cuda:1"), inputs[1].to("cuda:1")] + list(inputs[2:])))
model.decoder.register_forward_hook(lambda _, inputs, outputs: outputs.to("cuda:0"))

def error_log(message):
    with open('./error.log', 'a') as f:
        f.write(message)
        f.write('\n')

if __name__ == '__main__':
    start = time.time()  # 시작 시간 저장
    # meta csv를 로드한다.
    meta_df = pd.read_csv('meta_voice_data_3922.csv')
    print(meta_df)
    # wav파일은 로컬에 둔다. O
#df_hangul['cer_aws'] = df_hangul.apply(lambda row: nt.get_cer(row['ground_truth_hangul'], row['aws_trans'])['cer'],axis=1)
    prefix_name = './data/'
    ## 루프안에서
    for i in meta_df.index:
    #for i in range(1):
        try:
            # meta csv의 wav 파일명 칼람으로 실제 wav 파일이름을 변수에 설정하고 whisper transcribe를 돌린다.
            file_name = meta_df._get_value(i, 'file_name')
            file_path = str(os.path.join(prefix_name, file_name))
            #print(file_path)
            transcribe_sentence = model.transcribe(file_path)["text"]
            #print(transcribe_sentence)
            # 돌린 결과를 결과 칼럼에 넣는다.
            meta_df._set_value(i, 'transcribe_sentence', transcribe_sentence)
            # 돌린 결과와 정답의 CER 스코어를 계산한다.
            ground_truth_sentence = meta_df._get_value(i, 'ground_truth')
            #print('ground_truth_sentence : ', ground_truth_sentence)
            cer = nt.get_cer(ground_truth_sentence, transcribe_sentence)['cer']
            #print('CER : ', cer)
            # 계산한 CER를 CER 칼럼에 넣는다.
            meta_df._set_value(i, 'cer', cer)
        except Exception as e:
            error_log('faild_name : ' + str(e))


    meta_df.to_csv('./result/medium_result_3922.csv')
    elapsed_sec = time.time() - start  # 현재시각 - 시작시간 = 실행 시간
    elapsed_time = datetime.timedelta(seconds=elapsed_sec)

    error_log('Finish Job ')
    error_log(str(elapsed_time))
# 이거 모델마다 두번해야되지.... 아 함수로 뽑을까.