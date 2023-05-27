import json

def json_dump(file_name,data):
	with open(file_name,'w') as fw:
		json.dump(data,fw)
		fw.close()
def json_load(file_name):
	with open(file_name,'r') as fr:
		data=json.load(fr)
		fr.close()
	return data	