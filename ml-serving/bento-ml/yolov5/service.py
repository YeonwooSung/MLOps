import bentoml
from bentoml.io import Text

yolo_runner = bentoml.pytorch.get("pytorch_yolov5").to_runner()

svc = bentoml.Service(
    name="pytorch_yolo_demo",
    runners=[yolo_runner],
)


@svc.api(input=Text(), output=Text())
async def predict(img: str) -> str:
    assert isinstance(img, str)
    predictions = await yolo_runner.async_run(img)
    print(predictions)
    return predictions
