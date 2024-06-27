from keras.models import load_model
import pickle
from tensorflow import constant, float32, argmax
from sklearn.preprocessing import LabelEncoder



model = load_model("model.h5")

with open("tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)


tags = ['B-art', 'B-eve', 'B-geo', 'B-gpe', 'B-nat', 'B-org', 'B-per', 'B-tim', 'I-art', 'I-eve', 'I-geo', 'I-gpe', 'I-nat', 'I-org','I-per', 'I-tim', 'O', 'U']

encoder = LabelEncoder()
encoder.fit(tags)


def padSequence(sequence:list, maxLen:int, filler:int=0):
    if len(sequence) > maxLen:
        return sequence[:maxLen]
    totalZeros = maxLen - len(sequence) 
    return sequence + [filler for _ in range(totalZeros)]

def predictTags(text:str, maxLen:int, totalClasses:int):
    original = tuple((i, x, tokenizer.texts_to_sequences([x])[0]) for i, x in enumerate(text.split()))
    usable = tuple(x for x in original if len(x[-1]) > 0)

    tokens = constant([padSequence([x[-1][0] for x in usable], maxLen)], dtype=float32)
    prediction = argmax(model.predict(tokens, verbose=False), -1)[0].numpy().tolist()
    
    currentUsableIndex = 0
    paddedPredictions = []

    for x in range(len(original)):
        if len(original[x][-1]) > 0:
            paddedPredictions.append((original[x][1], encoder.inverse_transform([prediction[currentUsableIndex]])[0]))
            currentUsableIndex += 1
        else:
            paddedPredictions.append((original[x][1], encoder.inverse_transform([totalClasses-1])[0]))

    return paddedPredictions