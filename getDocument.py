
import pickle


def retrieve_by_docno(path, param):
    params = param.split("-")
    file_path = "/{}/{}/{}/{}.p".format(params[0][-2:], params[0][-6:-4], params[0][-4:-2], params[1])
    file_path = path + file_path
    with open(file_path, 'rb') as f:
        document = pickle.load(f)
        return document

def retrieve_by_id(path, param):
    with open(path + '/doc_id_no.p', 'rb') as file:
        doc_id_no = pickle.load(file)
        docno = doc_id_no[int(param)]
        return retrieve_by_docno(path, docno)
