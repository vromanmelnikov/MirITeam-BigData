import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

y = np.load('y.npy')
insert = y[-100:-70]

model = load_model('model.h5')
out = model.predict(insert.reshape(1, 30))[0][0]
pred = [out]
for i in range(29):
    insert = np.array(list(insert[1:].tolist()) + [out])
    out = model.predict(insert.reshape(1, 30))[0][0]
    pred.append(out)

y1 = np.array(pred)
y2 = y[-100:-40]

x1 = np.array([i for i in range(29, 59)])
x2 = np.array([i for i in range(60)])

plt.plot(x1, y1)
plt.plot(x2, y2)
plt.show()