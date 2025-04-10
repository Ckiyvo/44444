from ultralytics import YOLO
import supervision as sv
from PIL import Image
import numpy as np
import torch
from torchvision import models, transforms
import json

class ImageProcessor:
    def __init__(self):
        self.detect_model = YOLO(r'F:\a\apaper\project\project\algorithm\model\yolov8m.pt')
        self.classify_model = models.resnet50(pretrained=True)
        self.classify_model.eval()  # 设置为评估模式

    def preprocess_image(self, image):
        preprocess = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        image_tensor = preprocess(image)
        image_tensor = image_tensor.unsqueeze(0)  # 添加一个维度以匹配模型输入要求

        # 反归一化
        unnormalize = transforms.Normalize(
            mean=[-0.485 / 0.229, -0.456 / 0.224, -0.406 / 0.225],
            std=[1 / 0.229, 1 / 0.224, 1 / 0.225]
        )
        unnormalized_tensor = unnormalize(image_tensor.squeeze(0))
        # 将张量转换为 PIL 图像
        to_pil = transforms.ToPILImage()
        pil_image = to_pil(unnormalized_tensor)
        # 保存为 PNG 格式
        pil_image.save('preprocessed_image.png')

        return image_tensor

    def classify_image(self, image):
        image_tensor = self.preprocess_image(image)
        with torch.no_grad():
            output = self.classify_model(image_tensor)
        _, predicted = torch.max(output, 1)
        # 加载 ImageNet 标签
        with open(r'F:\a\apaper\project\project\algorithm\label\imagenet_classes.txt') as f:
            imagenet_labels = [line.strip() for line in f.readlines()]
        return imagenet_labels[predicted.item()]

    def object_detection(self, image):
        image = np.array(image)

        # 进行推理
        results = self.detect_model(source=image, conf=0.25, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)

        category_dict = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
            6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
            11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
            16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
            22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag',
            27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard',
            32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove',
            36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
            40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
            56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table',
            61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard',
            67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink',
            72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors',
            77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
        }

        detection_results = []
        for class_id, confidence, xyxy in zip(detections.class_id, detections.confidence, detections.xyxy):
            label = category_dict[class_id]
            result = {
                "label": label,
                "confidence": float(confidence),
                "bbox": xyxy.tolist()
            }
            detection_results.append(result)

        # 保存为 JSON 文件
        with open('detection_results.json', 'w') as f:
            json.dump(detection_results, f, indent=4)

        return detection_results


if __name__ == "__main__":
    image = Image.open(r'F:\a\apaper\project\project\algorithm\test_media\banana.jpg')
    processor = ImageProcessor()

    # 进行图像分类
    predicted_label = processor.classify_image(image)
    print(f"预测的类别是: {predicted_label}")

    processor.object_detection(image)