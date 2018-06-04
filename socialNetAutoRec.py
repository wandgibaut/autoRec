from keras.layers import Input, Dense
from keras.models import Model
from keras import regularizers
import keras.backend as K
import tensorflow as tf
import numpy as np
import random
from math import sqrt

def autoRec_loss(y_true,y_pred):
    zero = K.constant(0.0, dtype='float32')
    mask = K.not_equal(y_true, zero)
    return K.sum(K.square(tf.boolean_mask(y_true - y_pred, mask)), axis=-1)
        #y_true_rectified = tf.boolean_mask(tf.convert_to_tensor(y_true, dtype='float32'), mask)
    #y_pred_rectified = tf.boolean_mask(tf.convert_to_tensor(y_pred, dtype='float32'), mask)
    #return K.reduced_sum(K.square(y_true_rectified - y_pred_rectified), axis=-1)
    
    

        
def split_train_test(Input, Output):
    copyInput = np.copy(Input)
    copyInput = np.copy(Output)
    sliceX = round(len(Input)/10) # fatias de 10%
    in_test = np.full((sliceX,len(Input[0,:])),0.0)
    out_test = np.full((sliceX,len(Output[0,:])),0.0)
    #tira 10% pra teste. 10% dos individuos retirados COMPLETAMENTE. Preciso ainda separar em entrada e saida
    for i in range(sliceX):
        index = random.randrange(len(copyInput))
        in_test[i]= copyInput[index]
        np.delete(copyInput,index)

        out_test[i]= copyOutput[index]
        np.delete(copyOutput,index)

    #new_data= np.delete(copyData, test)

    train_in = copyInput
    train_out = copyOutput

    return [train_in, train_ouy, in_test, out_test]

#quebra o conjunto de validacao entre entrada e saida
def validation_split(val, percentage):
    val_entry = np.copy(val)
    val_expect = np.copy(val)

    for i in range(len(val)):
        entryObservations = np.nonzero(val[i,:]) # espero q sejam os indicies
        length = len(entryObservations[0])
        sliceX = round(length*percentage)

        for j in range(sliceX):
            index = random.randrange(length)
            val_entry[i,entryObservations[0][index]] = 0
            #length-=1

    return [val_entry, val_expect]

def test_accuracy(y_pred,y_true):
    mask = np.nonzero(y_true)
    y_pred_rectified = y_pred[mask]
    y_true_rectified = y_true[mask]
    return sqrt(sum((y_pred_rectified - y_true_rectified)**2)/len(y_true_rectified))
    #y_pred_rectified = y_pred[y_true > 0]
    #y_true_rectified = y_true[y_true > 0]
    
    #return K.mean(K.square(K.sum((y_true - y_pred))))



#list_of_files = [('../lastFM/fooData/foo.dat'), ('../lastFM/fooData/foo_friends.dat')]

#datalist = [(pylab.loadtxt(filename), label) for filename, label in list_of_files ]


if 1:
    Output = np.genfromtxt('../lastFM/fooData/foo.dat',
                     dtype=None,
                     delimiter=' ')

    in_put = np.genfromtxt('../lastFM/fooData/social_autoRec_input.dat',
                     dtype=None,
                     delimiter=' ')
    #print(data)

    

    if 1:
        #data = np.asarray(data[0])
        #print(data)
        input_size= len(in_put)
        input_dim = len(in_put[0,:])
        output_dim = len(Output[0,:])

        #print('sou lindo ')
        print(input_dim)
        print(input_size)



        encoding_dim = 50 #size of the encoding representation. Must tune this up

        #input_dim = 20000 #ver depois

        input_data = Input(shape=(input_dim,))

        #split NAO tah funfando direito
        [train_input, train_output, test_input, test_output] = split_train_test(in_put, Output)

        #print (len(train_input))        
        #print (len(test))



        encoded = Dense(encoding_dim, activation='sigmoid',activity_regularizer=regularizers.l2(1e-3))(input_data)
        #encoded = Dense(encoding_dim, activation='sigmoid', activity_regularizer=regularizers.l1(1e-5))(encoded)

        #decoded = Dense(round(input_dim/100), activation='sigmoid')(encoded)
        #decoded = Dense(round(input_dim/10), activation='sigmoid')(decoded)
        decoded = Dense(output_dim, activation='linear', activity_regularizer=regularizers.l2(1e-3))(encoded)
        #decoded = Dense(input_dim, activation='linear', activity_regularizer=regularizers.l1(1e-5))(decoded)

        #, kernel_regularizer=regularizers.l2(.1)

        #mapping
        autoencoder = Model(input_data, decoded)


        # ver documentação keras
        autoencoder.compile(optimizer='adadelta', loss=autoRec_loss) #'binary_crossentropy'

        ##
        #dados do treino, dividir em teste e treino corretamente
        #x_train= data
        #x_test = data


        autoencoder.fit(train_input, train_output,
                        epochs=1,
                        shuffle=True,
                        batch_size=1,#,#256,
                        #metrics=['mse'],
                        validation_split=0.1
                        )

# encode and decode some digits
# note that we take them from the *test* set

        
        [x_test, dummy] = validation_split(test_input, 0.2)

        y_test_pred = autoencoder.predict(x_test)
        #decoded_data = decoder.predict(encoded_data)

        autoencoder.evaluate(x_test, test_output)

        #print(encoded_data)

        print(max(x_test[0,:]))
        #print(max(x_test[1,:]))

        print(max(y_test_pred[0,:]))

        y_testinho = y_test[0,:]
        pred_test = y_test_pred[0,:]

        print(test_accuracy(y_test,y_test_pred))

        mask = np.nonzero(y_test[0,:])

        print(y_testinho[mask])
        print(pred_test[mask])