import numpy as np
import tensorflow.compat.v1 as tf
import cv2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


class object_dectection():
    def __init__(self,image_byte_array):
        self.MODEL_NAME = 'object_detection/inference_graph'
        self.PATH_TO_CKPT = self.MODEL_NAME + '/frozen_inference_graph.pb'
        self.PATH_TO_LABELS = 'object_detection/training/labelmap.pbtxt'
        self.NUM_CLASSES=32
        self.threshold = 0.60
        self.objects = []
        self.object_dict = {}
        self.image_array=image_byte_array

    def image_preprocess(self,image_array):
        img_arr=np.frombuffer(image_array, np.uint8)
        img_np = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        return img_np

    def run_model(self):
        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            sess = tf.Session(graph=detection_graph)

        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        image =self.image_preprocess(self.image_array)
        image_rgb=image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_expanded = np.expand_dims(image_rgb, axis=0)
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})
        vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)

        for index, value in enumerate(classes[0]):
          if scores[0, index] > self.threshold:
            self.object_dict[(category_index.get(value)).get('name').encode('utf8')] = \
                                scores[0, index]
            self.objects.append(self.object_dict)

        return self.objects

