import torch
from torch import nn
from pathlib import Path

import bentoml

from models.common import DetectMultiBackend
from utils.torch_utils import select_device, time_sync
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages
from utils.general import check_file, check_img_size, non_max_suppression, scale_boxes


# Model
device = select_device('')
original_model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)
original_model.eval()


class WrapperModel(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, imgs):
        source = str(imgs)
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        if is_url and is_file:
            source = check_file(source)  # download

        # Load model
        device = select_device('')
        stride, names, pt = self.model.stride, self.model.names, self.model.pt
        imgsz = check_img_size((448, 448), s=stride)  # check image size

        half = False
        if pt:
            self.model.model.half() if half else model.model.float()

        # Dataloader
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
        bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs

        # Run inference
        dt, seen = [0.0, 0.0, 0.0], 0
        for path, im, im0s, vid_cap, s in dataset:
            t1 = time_sync()
            im = torch.from_numpy(im).to(device)
            im = im.half() if half else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            t2 = time_sync()
            dt[0] += t2 - t1

            # Inference
            pred = self.model(im)
            t3 = time_sync()
            dt[1] += t3 - t2

            # NMS
            if torch.cuda.is_available():
                pred = non_max_suppression(prediction=pred, conf_thres=torch.tensor(0.25).cuda(), iou_thres=torch.tensor(0.45).cuda(), classes=None, agnostic=False, max_det=1000)
            else:
                pred = non_max_suppression(prediction=pred, conf_thres=torch.tensor(0.25), iou_thres=torch.tensor(0.45), classes=None, agnostic=False, max_det=1000)
            dt[2] += time_sync() - t3

            # Process predictions
            for i, det in enumerate(pred):  # per image
                seen += 1
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

                s += '%gx%g ' % im.shape[2:]  # print string
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
        return s


model = WrapperModel(original_model)

# save pytorch model for BentoML
saved_model = bentoml.pytorch.save_model('pytorch_yolov5', model)
print(f"Model saved: {saved_model}")
