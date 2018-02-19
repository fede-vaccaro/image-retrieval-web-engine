from keras import Model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
import h5py
import time

datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

input_shape = (224, 224, 3)
model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=True)
t1 = time.time()
layer_name = "fc2"
intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer(layer_name).output)

batch_size = 32

gen = datagen.flow_from_directory("img_windowed", target_size=(224,224), class_mode=None, shuffle=False)


t1 = time.time()
results = intermediate_layer_model.predict_generator(gen, verbose=True)
t2 = time.time()

print("{0} element generated in {1}s".format(results.shape[0], t2-t1))

print("Saving results on feature_matrix_with_windows.h5")
h5f = h5py.File("feature_matrix_with_windows.h5", 'w')

total_image = 256
n_window = 500

for i in range(total_image):
    h5f.create_dataset('feature_matrix_image_{}'.format(i), data=results[i*n_window:(i+1)*n_window+1])

h5f.close()
print("Result saved. Closing...")