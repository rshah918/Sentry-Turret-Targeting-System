#utility scripts for NN processing

import numpy as np
from PIL import Image
import cv2
import tflite_runtime.interpreter as tflite
import collections
import platform

## utilities specific to Tflite and EdgeTPU
Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])
class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """
    __slots__ = ()
EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

def make_interpreter(model_file):
    model_file, *device = model_file.split('@')
    return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[
          tflite.load_delegate(EDGETPU_SHARED_LIB,
                               {'device': device[0]} if device else {})
      ])

def set_input(interpreter, image, resample=Image.NEAREST):
    """Copies data to input tensor."""
    image = image.resize((input_image_size(interpreter)[0:2]), resample)
    #image = np.resize(image,(input_image_size(interpreter)[0:3]))
    input_tensor(interpreter)[:, :] = image

def input_image_size(interpreter):
    """Returns input image size as (width, height, channels) tuple."""
    _, height, width, channels = interpreter.get_input_details()[0]['shape']
    return width, height, channels

def input_tensor(interpreter):
    """Returns input tensor view as numpy array of shape (height, width, 3)."""
    tensor_index = interpreter.get_input_details()[0]['index']
    return interpreter.tensor(tensor_index)()[0]

def output_tensor(interpreter, i):
    """Returns dequantized output tensor if quantized before."""
    output_details = interpreter.get_output_details()[i]
    output_data = np.squeeze(interpreter.tensor(output_details['index'])())
    if 'quantization' not in output_details:
        return output_data
    scale, zero_point = output_details['quantization']
    if scale == 0:
        return output_data - zero_point
    return scale * (output_data - zero_point)

def get_output(interpreter, score_threshold, top_k, image_scale=1.0):
    """Returns list of detected objects."""
    boxes = output_tensor(interpreter, 0)
    class_ids =output_tensor(interpreter, 1)
    scores = output_tensor(interpreter, 2)
    count = int(output_tensor(interpreter, 3))

    def make(i):
        ymin, xmin, ymax, xmax = boxes[i]
        return Object(
            id=int(class_ids[i]),
            score=scores[i],
            bbox=BBox(xmin=np.maximum(0.0, xmin),
                        ymin=np.maximum(0.0, ymin),
                        xmax=np.minimum(1.0, xmax),
                        ymax=np.minimum(1.0, ymax)))

    return [make(i) for i in range(top_k) if scores[i] >= score_threshold and class_ids[i]==0]
def append_objs_to_img(cv2_im, objs, labels):
    height, width, channels = cv2_im.shape
    for obj in objs:
        x0, y0, x1, y1 = list(obj.bbox)
        x0, y0, x1, y1 = int(x0*width), int(y0*height), int(x1*width), int(y1*height)
        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, obj.id)

        cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    return cv2_im

def calculate_pixel_deltas(frame, result,correction_threshold=0):
    '''For each BB in result[], calculate how many pixels the center of each BB is
        from the center of the image, and return them in an array.
    Returns: 1D array of [deltaX,deltaY] pairs'''
    deltas = []
    height, width, channels = frame.shape
    for obj in result:
        x0, y0, x1, y1 = list(obj.bbox)
        x0, y0, x1, y1 = int(x0*width), int(y0*height), int(x1*width), int(y1*height)
            #width and height of BB
        BBwidth = abs(round(x1-x0))
        BBheight = abs(round(y1-y0))
            #center of BB
        BBcenterX = x0 + round(BBwidth/2)
        BBcenterY = y0 + round(BBheight/2)
        #center of image
        imageCenterX = round(width/2)
        imageCenterY = round(height/2)
        #calculate deltas
            #negative delta means target is offset below/left of center
        deltaX = BBcenterX - imageCenterX
        deltaY = imageCenterY - BBcenterY
        if abs(deltaX) < correction_threshold:
                deltaX = 0
        if abs(deltaY) < correction_threshold:
            deltaY = 0
        deltas.append([deltaX, deltaY, BBwidth, BBheight])
        print(BBcenterX, BBcenterY,
            imageCenterX, imageCenterY, deltaX, deltaY)
    return deltas