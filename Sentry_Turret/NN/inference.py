# this script runs inference on the TPU for a given model and classes
import cv2
import NN.utils as utils
import numpy as np
from PIL import Image
import os
import tflite_runtime.interpreter as tflite

# The utils_sentry_inference API 
    # run_inference()
        # input: np array of frame
        # optionals: specific model file, characteristics of high priority target
        # outputs: pixel deltas of the highest priority object from frame center
    # run_inference_to_Boxes()
        # gives you back the raw boxes so you can do more processing

# initialize the model (using default model)
class InferenceTPU:
    def __init__(self):
        self.model_file = "NN/Tflite_Models/ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite"
        self.interpreter = utils.make_interpreter(self.model_file)
        self.interpreter.allocate_tensors()
        print("NN loaded")
    def run_inference(self,image):
        nn_im = Image.fromarray(image)
        utils.set_input(self.interpreter, nn_im)
        self.interpreter.invoke()
        #print(utils.output_tensor(self.interpreter,0))
        objs = utils.get_output(self.interpreter, score_threshold=.65, top_k=3)
        image = utils.append_objs_to_img(image,objs,None)
        # calculate the frame deltas
        deltas = utils.calculate_pixel_deltas(image,objs)
        return (deltas,image)