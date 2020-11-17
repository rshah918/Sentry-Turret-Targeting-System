from darkflow.net.build import TFNet
import cv2
import time
import math
import serial
'''
Targeting Software for our CSCE-462 Sentry Turret
Workflow:
    1: Camera input->Neural Net (Human Detector)
    2: NMS
    3: Select 1 bounding box as target
    4: Calculate pan/tilt deltas to aim the turret
    5: Send motor coordinates to the Arduino motor controller
    6: Fire turret
'''
def load_network(experimental_detector=False):
    '''Loads neural net from protobuf and meta file
        Params: experimental_detector is a smaller neural net with a custom modified
        architecture, ~33% faster (~30FPS on CPU)
        Default neural net is an unmodified tiny-yolo architecture, ~21 FPS on CPU
        Returns: initialized neural net
    '''
    #
    if experimental_detector == True:
        protobuf_path = "built_graph/super-tiny-yolo-human.pb"
        meta_path = "built_graph/super-tiny-yolo-human.meta"
    else:
        protobuf_path = "built_graph/tiny-yolo-human.pb"
        meta_path = "built_graph/tiny-yolo-human.meta"
    options = {"pbLoad": protobuf_path, "metaLoad": meta_path, "threshold": 0.1}
    tfnet = TFNet(options)
    return tfnet

def downscale_image(frame, scale_percent=100):
    '''Resize input frame's dimensions to X% of its original size
        while maintaining aspect ratio'''
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    return frame

def draw_bounding_box(frame, result):
    '''display all detected bounding boxes'''
    if len(result) > 0:
        for i in range(len(result)):
            img = cv2.rectangle(frame, (result[i]['topleft']['x'],result[i]['topleft']['y']), (result[i]['bottomright']['x'], result[i]['bottomright']['y']), (255,0,0), 2)

def calculate_pixel_deltas(frame, result, correction_threshold = 0):
    '''For each BB in result[], calculate how many pixels the center of each BB is
        from the center of the image, and return them in an array.
    Returns: 1D array of [deltaX,deltaY] pairs'''
    deltas = []
    if len(result) > 0:
        for i in range(len(result)):
            #width and height of BB
            BBwidth = abs(round((result[i]['bottomright']['x'] - result[i]['topleft']['x'])))
            BBheight = abs(round((result[i]['bottomright']['y'] - result[i]['topleft']['y'])))
            #center of BB
            BBcenterX = result[i]['topleft']['x'] + round(BBwidth/2)
            BBcenterY = result[i]['bottomright']['y'] - round(BBheight/2)
            #center of image
            imageCenterX = round(len(frame[0])/2)
            imageCenterY = round(len(frame)/2)
            #calculate deltas
                #negative delta means target is offset below/left of center
            deltaX = BBcenterX - imageCenterX
            deltaY = imageCenterY - BBcenterY
            #Set delta to 0 if object is "close enough" to the center to reduce jitter
            if abs(deltaX) < correction_threshold:
                deltaX = 0
            if abs(deltaY) < correction_threshold:
                deltaY = 0
            deltas.append([deltaX, deltaY, BBwidth, BBheight])
            print(BBcenterX, BBcenterY,
             imageCenterX, imageCenterY, deltaX, deltaY)
    return deltas

def select_target(pixel_deltas=[]):
    '''Calculate the Euclidean Distance between the image center and each detected human.
        Selects the closest human to the center of the frame as the target'''
    selected_target = []
    if(len(pixel_deltas) > 0):
        largest_target = 0
        min_distance = 999
        for target in pixel_deltas:
            deltaX = target[0]
            deltaY = target[1]
            targetWidth = target[2]
            targetHeight = target[2]
            targetSize = targetWidth*targetHeight
            euclideanDistance = math.sqrt((deltaX**2)+(deltaY**2))
            '''if euclideanDistance < min_distance:
                selected_target = [deltaX, deltaY]'''
            if targetSize > largest_target:
                selected_target = [deltaX, deltaY]
    return selected_target

def calculate_motor_deltas(pixel_deltas=[]):
        '''Pixel delta to motor degree rotation conversion
            Returns: [pan,tilt]'''
        motor_deltas = []
        if len(pixel_deltas) > 0:
            '''Mark, enter the pixel delta->motor delta conversion code here
            return a 1D array: [pan,tilt]
            '''
            pass
        return motor_deltas

def aim_turret(motor_deltas=[]):
        '''Send aiming coordinates to pan/tilt motors over serial connection to Arduino'''
        if len(motor_deltas) > 0:
            pan = motor_deltas[0]
            tilt = motor_deltas[1]
            ser.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))

tfnet = load_network(experimental_detector=True)
cap = cv2.VideoCapture(0)
curr = time.time()
num_frames = 0
skip = 0
while True:
    #skip every other frame
    if skip == 1:
        skip = 0
        num_frames += 1
        continue
    else:
        skip += 1
    #grab video frame
    ret, frame = cap.read()
    #downscale input frame
    frame = downscale_image(frame, 100)
    #forward propagate
    result = tfnet.return_predict(frame)
    #draw bounding boxes
    draw_bounding_box(frame,result)
    #calculate deltas
    correction_threshold = 100
    deltas = calculate_pixel_deltas(frame, result, correction_threshold)
    #select target
    target = select_target(deltas)
    #calculate motor rotation coordinates
    motor_deltas = calculate_motor_deltas(target)
    #aim gun
    aim_turret(motor_deltas)
    #FPS tracking
    num_frames += 1
    now = time.time()
    if now-curr >= 1:
        print("ML Inference at: ", num_frames, " FPS")
        num_frames = 0
        curr = now
    #display the image and bounding box
    cv2.imshow('frame', frame)
    #Kill program with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'): #kill with q key
        break

# When everything's done, release the capture
cap.release()
cv2.destroyAllWindows()
