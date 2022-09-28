import nlptutti as nt
from trans_util.transcribe_util import start_job, read_dataframe_metadata, get_transcribe_sentence, api_error_log, read_txt


aa = read_txt('./groundtruth/1_PB 수신고객응대_정답지.txt')
print("?? : ", aa)