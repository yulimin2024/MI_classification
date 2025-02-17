# -*- coding: utf-8 -*-
"""Magic_supervised.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1O0vj32Cnixs_bOryc2xuGQ6IzWWejkUp

# Magic Gamma Telescope Practice
"""

# Module import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""# Dataset

**Dataset loading**
* https://archive.ics.uci.edu/dataset/159/magic+gamma+telescope
"""

# google colab 업로드해서 데이터 csv 화일 읽기
from google.colab import files
uploaded=files.upload()

df=pd.read_csv('magic04.data')

# 컬럼명칭 생성
cols=['fLength','fWidth','fSize','fConc','fConc1','fAsym','fM3Long','fM3Trans','fAlpha','fDist','class']
df.columns=cols
df.head()

#[class 라벨] 문자 -> 숫자 변경
df['class'].unique()

# binary classification: g->1, h->0
df['class']=(df['class']=='g').astype(int)
df['class'].unique()

df.head()

"""**features 간의 관계 보기**"""

for feature in cols[:-1]: #class 라벨은 제외
  plt.hist(df[df['class']==1][feature], color='blue', label='gamma', alpha=0.7, density=True)
  plt.hist(df[df['class']==0][feature], color='red', label='hardon', alpha=0.7, density=True)
  plt.title(feature)
  plt.ylabel('Probability')
  plt.xlabel(feature)
  plt.legend()
  plt.show()

"""**Dataset -> Train/Valdiation/Test**"""

cutoff=[int(len(df)*0.6), int(len(df)*0.8)]
train, valid, test = np.split(df.sample(frac=1), cutoff)
train.shape, valid.shape, test.shape

"""**데이터 정규화 + 오버샘플링**
* 데이터 정규화: 평균 0, 표준편차 1
* 오버샘플링: 라벨 데이터 개수를 균일하게 만들기 위해 오버샘플링
"""

# 라벨에 따른 데이터 개수 확인 -> oversample 필요?
print((train['class']==1).sum()) # class 1라벨 데이터 개수
print((train['class']==0).sum()) # class 0 라벨 데이터 개수

# 모듈 import
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler

# 정규화 + 오버샘플링 함수 생성
def scale_dataset(dataframe, oversample=False):
  X=dataframe[dataframe.columns[:-1]].to_numpy() #넘파이로 변환
  y=dataframe[dataframe.columns[-1]].to_numpy()

  #객체생성
  scaler=StandardScaler()
  X_scaled=scaler.fit_transform(X)

  #오버샘플링
  if oversample:
    ros=RandomOverSampler()
    X_scaled, y=ros.fit_resample(X_scaled, y)

  #X, y 병합
  data=np.hstack((X_scaled, y.reshape(-1,1))) #hstack은 tuple로 받음 () 주의!

  #data, X_scaled, y 반환
  return data, X_scaled, y

# 정규화+오버샘플링된 train/validation/test
train, X_train, y_train=scale_dataset(train, oversample=True)
valid, X_valid, y_valid=scale_dataset(valid, oversample=False)
test, X_test, y_test=scale_dataset(test, oversample=False)

"""# Training

**KNN**
"""

# module import
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report

# 모델생성
knn_model=KNeighborsClassifier(n_neighbors=5) #n_neighbors 인자 지정
knn_model.fit(X_train, y_train)

# 예측
y_pred=knn_model.predict(X_test)
y_pred

print(classification_report(y_test, y_pred)) #print 함수를 써야 아래와 같이 출력됨. 왜(?)

"""**Naive Bayes**"""

# module import
from sklearn.naive_bayes import GaussianNB

#모듈 생성
nb_model=GaussianNB()
#학습
nb_model.fit(X_train, y_train)

#예측
y_pred=nb_model.predict(X_test)

#평가
print(classification_report(y_test, y_pred))

"""** Logistic Regression **"""

# module import
from sklearn.linear_model import LogisticRegression

# 객체 생성
lr_model=LogisticRegression()
# 학습
lr_model.fit(X_train, y_train)

# 예측
y_pred=lr_model.predict(X_test)

# 평가
print(classification_report(y_test,y_pred))

"""**SVM**"""

from sklearn.svm import SVC

svm_model=SVC()
svm_model.fit(X_train, y_train)

y_pred=svm_model.predict(X_test)
print(classification_report(y_test, y_pred))

"""**Neural Net**"""

import tensorflow as tf

# history plot
def plot_history(history):
  plt.figure(figsize=(10,4))
  plt.subplot(1,2,1)
  plt.plot(history.history['loss'], label='loss')
  plt.plot(history.history['val_loss'], label='val_loss')
  plt.legend()

  plt.subplot(1,2,2)
  plt.plot(history.history['accuracy'], label='accuracy')
  plt.plot(history.history['val_accuracy'], label='val_accuracy')
  plt.legend()

  plt.show()

# nn_model, history 반환 함수 생성
def train_model(X_train, y_train, num_nodes, dropout_rate, lr, batch_size, epochs):
  nn_model=tf.keras.Sequential([
      tf.keras.layers.Dense(num_nodes, activation='relu', input_shape=(10,)),
      tf.keras.layers.Dropout(dropout_rate),
      tf.keras.layers.Dense(num_nodes, activation='relu'),
      tf.keras.layers.Dropout(dropout_rate),
      tf.keras.layers.Dense(1, activation='sigmoid')
])
  # compile 필요
  nn_model.compile(optimizer=tf.keras.optimizers.Adam(lr),
                 loss='binary_crossentropy',
                 metrics=['accuracy'])

  # 모델 객체 생성
  history=nn_model.fit(X_train, y_train,
                       epochs=100, batch_size=32,
                       validation_data=(X_valid, y_valid), verbose=0)

  return nn_model, history

epochs=10
num_nodes=16
dropout_rate=0.2
lr=0.01
batch_size=32
nn_model, history=train_model(X_train, y_train,
                                      num_nodes, dropout_rate, lr, batch_size, epochs)

plot_history(history)

#예측
y_pred=nn_model.predict(X_test)
y_pred=(y_pred>0.5).astype(int) # y_pred는 확률값 가지므로 범주형으로 변환
y_pred=y_pred.reshape(-1,) # y_pred는 2차원(n,1) -> 1차원 변환
y_pred

#평가
print(classification_report(y_test, y_pred))

"""**Neural Net Experiment- Hyperparameter tunning**"""

# Experiments

least_val_loss=float('inf')
least_loss_model=None

epochs=10
for num_nodes in [16,32,64]:
  for dropout_rate in [0, 0.2]:
    for lr in [0.01, 0.005, 0.001]:
      for batch_size in [32, 64, 128]:
        print(f"{num_nodes} nodes, dropout {dropout_rate}, lr {lr}, batch_size {batch_size}")

        model, history=train_model(X_train, y_train,
                                      num_nodes, dropout_rate, lr, batch_size, epochs)
        plot_history(history)
        val_loss=model.evaluate(X_valid, y_valid)[0]
        if val_loss<least_val_loss:
          least_val_loss=val_loss
          least_loss_model=model

#Best model
y_pred_opt=least_loss_model.predict(X_test)
y_pred_opt=(y_pred_opt>0.5).astype(int) # y_pred는 확률값 가지므로 범주형으로 변환
y_pred_opt=y_pred_opt.reshape(-1,) # y_pred는 2차원(n,1) -> 1차원 변환

# 최적화 값
print(classification_report(y_test, y_pred_opt))