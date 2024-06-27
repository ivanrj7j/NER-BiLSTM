import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer

def splitText(dataFrame: pd.DataFrame) -> pd.DataFrame:
    dataFrame.text = dataFrame.text.apply(lambda x: x.split())
    dataFrame.labels = dataFrame.labels.apply(lambda x: x.split())
    # splits the dataframe into lists instead of strings 
    
    return dataFrame

def getEncoder(dataFrame: pd.DataFrame) -> LabelEncoder:
    labelEncoder = LabelEncoder()
    labelEncoder.fit(["U"] + list(set(dataFrame.labels.explode())))

    return labelEncoder

def labelEncodeDataFrame(dataFrame: pd.DataFrame, labelEncoder:LabelEncoder) -> pd.DataFrame:
    dataFrame.labels = dataFrame.labels.apply(lambda x: labelEncoder.transform(x))
    return dataFrame

def getTokenizer(dataFrame:pd.DataFrame) -> Tokenizer:
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(dataFrame.text.explode("text").to_list())
    # initializing the tokenizer 

    return tokenizer

def sequence(wordList:list, tokenizer:Tokenizer):
    seq = tokenizer.texts_to_sequences(wordList)
    return seq

def padSequence(sequence:list, maxLen:int, filler:int=0):
    if len(sequence) > maxLen:
        return sequence[:maxLen]
    totalZeros = maxLen - len(sequence) 
    return sequence + [filler for _ in range(totalZeros)]
# pad function 

def prepareData(sequence:list[list], tags:list, unknownFiller:int):
    newTags = []
    newSequence = []
    for i, s in enumerate(sequence):
        if len(s) == 0:
            newTags.append(unknownFiller)
            newSequence.append(0)
        else:
            for item in s:
                newTags.append(tags[i])
                newSequence.append(item)
                
    return newTags, newSequence

def preparePaddedData(sequence:list[list], tags:list, unknownFiller:int, maxLen:int, totalClasses:int):
    tags, sequence = prepareData(sequence, tags, unknownFiller)
    newTags = padSequence(tags, maxLen)
    newSequence = padSequence(sequence, maxLen)
    
    return newSequence, tf.one_hot(newTags, totalClasses)

def prepareDataFrame(fileName:str, split=True, splitRatio:float=0.85) -> pd.DataFrame | tuple[pd.DataFrame]:
    df = pd.read_csv(fileName)
    df = splitText(df)
    df = labelEncodeDataFrame(df, getEncoder(df))

    if split:
        df = df.sample(frac=1)
        splitIndex = int(df.shape[0] * splitRatio)
        train = df.iloc[:splitIndex].reset_index(drop=True)
        test = df.iloc[splitIndex:].reset_index(drop=True)
        return train, test
    else:
        return df
    

def dataGenerator(df:pd.DataFrame,tokenizer:Tokenizer,maxLen:int, totalClasses:int, fields=("text", "labels")):
    for x, y in zip(df[fields[0]], df[fields[1]]):
        
        s, t = preparePaddedData(sequence(x, tokenizer), y, totalClasses-1, maxLen, totalClasses)
        
        yield tf.constant(s, dtype=tf.float32), tf.constant(t, dtype=tf.float32)

def getTensorflowDataset(df:pd.DataFrame,tokenizer:Tokenizer,maxLen:int, totalClasses:int, fields=("text", "labels"), batchSize=64):
    dataset = tf.data.Dataset.from_generator(lambda : dataGenerator(df, tokenizer, maxLen, totalClasses, fields), output_signature=(
        tf.TensorSpec(shape=(maxLen,), dtype=tf.float32),
        tf.TensorSpec(shape=(maxLen, totalClasses), dtype=tf.float32),
    )).batch(batchSize)
    return dataset