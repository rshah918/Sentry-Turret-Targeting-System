'''
Convert a protobuf tensorflow model to TFlite in prep for inference on the Coral TPU hardware accelerator
'''

'''
CLI command: tflite_convert --graph_def_file='tiny-yolo-human.pb' --output_file='yolov2-tiny.lite' --input_format=TENSORFLOW_GRAPHDEF --output_format=TFLITE --input_shape=1,416,416,3 --input_array=input --output_array=output

'''
