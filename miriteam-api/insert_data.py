def get_pred(data: list, pred_days: int):
    import numpy as np
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from tensorflow import keras
    from keras.models import load_model

    insert = np.array(data)
    model = load_model('model.h5')
    out = model.predict(insert.reshape(1, 30))[0][0]
    pred = [out]
    for i in range(pred_days-1):
        insert = np.array(list(insert[1:].tolist()) + [out])
        out = model.predict(insert.reshape(1, 30))[0][0]
        pred.append(out)
    for i in range(len(pred)):
        pred[i] = int(pred[i])
    
    return pred