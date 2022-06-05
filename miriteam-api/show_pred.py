import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

y = np.load('y.npy')
insert = y[-60:-30]

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

# pred_days = 30

# y1 = np.array(get_pred(insert, pred_days))
# y2 = y[-100:]

# x1 = np.array([i for i in range(70, 70+pred_days)])
# x2 = np.array([i for i in range(100)])

# plt.plot(x2, y2)
# plt.plot(x1, y1)
# plt.show()