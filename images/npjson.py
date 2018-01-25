import codecs, json
import numpy as np


class JSONVectConverter():

    def vect_to_json(nparray):
        json_text = json.dumps(nparray.tolist(), sort_keys=True, indent=4)  ### this saves the array in .json format
        return json_text

    def json_to_vect(jsonStr):
        vect = np.array(json.loads(jsonStr))
        return vect

    def save_vect_to_json(filepath, nparray):
        path = filepath + ".json"
        json.dump(nparray.tolist(), codecs.open(path, 'w', encoding='utf-8'), separators=(',', ':'),
                  sort_keys=True)
        return

    def open_json_to_vect(filepath):
        obj_text = codecs.open(filepath, 'r', encoding='utf-8').read()
        new_vect = np.array(json.loads(obj_text))
        return new_vect


""" ------ Some Example
V1 = [1., 2.123, 3.10928740, 7.92]
a = np.array(V1).reshape([2, 2]).tolist()
file_path = "pathA.json"
json.dump(a, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True,
          indent=4)  ### this saves the array in .json format

V2 = [2., 0.12, 0.30, 0.08]
b = np.array(V2).reshape([2, 2]).tolist()
file_path = "pathB.json"
X = json.dumps(b, sort_keys=True, indent=4)  ### this saves the array in .json format
print(X)
a_new = json.loads(X)
print(a_new)
a_new = np.array(a_new)
print(a_new)


obj_text = codecs.open("pathA.json", 'r', encoding='utf-8').read()
a_new = json.loads(obj_text)
a_new = np.array(a_new)

obj_text = codecs.open("pathB.json", 'r', encoding='utf-8').read()
b_new = json.loads(obj_text)
b_new = np.array(b_new)

c_new = np.dot(a_new.reshape([4]), b_new.reshape([4]))

file_path = "pathC.json"
json.dump(c_new.tolist(), codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4) ### this saves the array in .json format
"""
