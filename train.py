from preprocess import generate_training_sequences, SEQUENCE_LENGTH
import tensorflow.keras as keras
import matplotlib.pyplot as plt
OUTPUT_UNITS = 12
NUM_UNITS = [256]
LOSS = "sparse_categorical_crossentropy"
LEARNING_RATE = 0.001
EPOCHS = 50
BATCH_SIZE = 4
#SAVE_MODEL_PATH = "model.h5"


def build_model(output_units, num_units, loss, learning_rate):
    #create the model architecture
    input = keras.layers.Input(shape=(None, output_units))
    x = keras.layers.LSTM(num_units[0])(input)
    x = keras.layers.Dropout(0.2)(x)
    output = keras.layers.Dense(output_units, activation="softmax")(x)
    model = keras.Model(input, output) 
    #compile the model
    model.compile(loss=loss, optimizer=keras.optimizers.Adam(lr=learning_rate),
                  metrics=["accuracy"])
    
    model.summary()

    return model


def train(output_units=OUTPUT_UNITS, num_units=NUM_UNITS, loss=LOSS, learning_rate=LEARNING_RATE):
    #initialize lists to store loss and accuracy values
    lstm_loss = []
    accuracy = []
    
    #generate training sequences
    inputs, targets = generate_training_sequences(SEQUENCE_LENGTH)

    # build the network
    model = build_model(output_units, num_units, loss, learning_rate)
    for epoch in EPOCHS:
        # train the model 
        model_loss, accuracy_epoch = model.fit(inputs, targets, epoch=1, batch_size=BATCH_SIZE)
        lstm_loss.append(model_loss)
        accuracy.append(accuracy_epoch)
        
        #save the model every 10 epochs
        if (epoch+1)//10 == 0:
            model.save(f"lstm_epoch{epoch}.h5")
    
    return lstm_loss, accuracy 


def plot(loss, accuracy):
  y_1 = loss
  y_2 = accuracy
  #x = history["epochs"]
  # plot
  plt.plot(y_1)
  plt.plot(y_2)
  plt.xlabel('epoch')
  plt.legend(['loss', 'acuraccy'], loc='center right')

  plt.show()

plot(history = histroy)

if __name__ == "__main__":
    loss, accuracy = train()
    plot(loss=loss, accuracy=accuracy)
    


