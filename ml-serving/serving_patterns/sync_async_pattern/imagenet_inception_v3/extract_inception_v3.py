import json
from typing import Dict, List

import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras


def get_label(json_path: str = "./data/image_net_labels.json") -> List[str]:
    with open(json_path, "r") as f:
        labels = json.load(f)
    return labels


def load_hub_model() -> tf.keras.Model:
    model = tf.keras.Sequential([hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_v3/classification/4")])
    model.build([None, 299, 299, 3])
    return model


class InceptionV3Model(tf.keras.Model):
    def __init__(self, model: tf.keras.Model, labels: List[str]):
        super().__init__(self)
        self.model = model
        self.labels = labels

    @tf.function(input_signature=[tf.TensorSpec(shape=[None], dtype=tf.string, name="image")])
    def serving_fn(self, input_img: str) -> tf.Tensor:
        def _base64_to_array(img):
            img = tf.io.decode_base64(img)
            img = tf.io.decode_jpeg(img)
            img = tf.image.convert_image_dtype(img, tf.float32)
            img = tf.image.resize(img, (299, 299))
            img = tf.reshape(img, (299, 299, 3))
            return img

        img = tf.map_fn(_base64_to_array, input_img, dtype=tf.float32)
        predictions = self.model(img)

        def _convert_to_label(predictions):
            max_prob = tf.math.reduce_max(predictions)
            idx = tf.where(tf.equal(predictions, max_prob))
            label = tf.squeeze(tf.gather(self.labels, idx))
            return label

        return tf.map_fn(_convert_to_label, predictions, dtype=tf.string)

    def save(self, export_path="./saved_model/inception_v3/"):
        signatures = {"serving_default": self.serving_fn}
        tf.keras.backend.set_learning_phase(0)
        tf.saved_model.save(self, export_path, signatures=signatures)


def main():
    labels = get_label(json_path="./data/image_net_labels.json")
    inception_v3_hub_model = load_hub_model()
    inception_v3_model = InceptionV3Model(model=inception_v3_hub_model, labels=labels)
    version_number = 0
    inception_v3_model.save(export_path=f"./saved_model/inception_v3/{version_number}")


if __name__ == "__main__":
    main()
