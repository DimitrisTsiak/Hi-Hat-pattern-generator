# machine-learning
# hi-hat pattern midi generator
This project allows you to create rythmic hihat patterns in the style of hip-hop music 
## Requirements

* Python 3.x
* Packages
  * Music21
  * Keras
  * Tensorflow

## Training
to train the network run "train.py"

If you want to train the network on you own midi data, make sure that they only contain monophonic patterns, without subdivisions or multiples of triplets.


## Generating patterns

Once you have trained the network you can generate patterns using **pattern_generator.py**

You can run the prediction file with thepretrained model by using the **model.h5** file

