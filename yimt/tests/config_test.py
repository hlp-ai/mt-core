import copy
import filecmp
import os

import tensorflow as tf
import yaml

from parameterized import parameterized

from yimt import config
from yimt.models.model import Model


class ConfigTest(tf.test.TestCase):
    def testConfigOverride(self):
        config1 = {
            "model_dir": "foo",
            "train": {"batch_size": 32, "steps": 42},
            "params": {
                "optimizer": "Adam",
                "optimizer_params": {"beta_1": 0.9, "beta_2": 0.998},
            },
        }
        config2 = {
            "model_dir": "bar",
            "train": {"batch_size": 64},
            "params": {"optimizer": "SGD", "optimizer_params": {}},
        }
        config_file_1 = os.path.join(self.get_temp_dir(), "config1.yml")
        config_file_2 = os.path.join(self.get_temp_dir(), "config2.yml")

        with open(config_file_1, mode="w") as config_file:
            config_file.write(yaml.dump(config1))
        with open(config_file_2, mode="w") as config_file:
            config_file.write(yaml.dump(config2))

        loaded_config = config.load_config([config_file_1, config_file_2])

        self.assertDictEqual(
            {
                "model_dir": "bar",
                "train": {"batch_size": 64, "steps": 42},
                "params": {"optimizer": "SGD", "optimizer_params": {}},
            },
            loaded_config,
        )

    def _writeCustomModel(self, filename="test_model.py", return_value=42):
        model_path = os.path.join(self.get_temp_dir(), filename)
        with open(model_path, mode="w") as model_file:
            model_file.write("model = lambda: %d" % return_value)
        return model_path

    def testLoadModelModule(self):
        model_path = self._writeCustomModel()
        model_module = config.load_model_module(model_path)
        model = model_module.model()
        self.assertEqual(42, model)

    def testLoadModelFromCatalog(self):
        model_name = "Transformer"
        model = config.load_model_from_catalog(model_name)
        self.assertIsInstance(model, Model)

    @parameterized.expand(
        [
            ("Transformer", False),
            ("TransformerBase", True),
        ]
    )
    def testLoadModel(self, model_name, as_builder):
        def _check_model(model):
            if as_builder:
                self.assertTrue(model, callable)
                model = model()
            self.assertIsInstance(model, Model)

        model_dir = self.get_temp_dir()
        _check_model(
            config.load_model(model_dir, model_name=model_name, as_builder=as_builder)
        )
        self.assertTrue(
            os.path.exists(os.path.join(model_dir, config.MODEL_DESCRIPTION_FILENAME))
        )
        _check_model(config.load_model(model_dir, as_builder=as_builder))

    def testLoadModelDescriptionCompat(self):
        model_dir = self.get_temp_dir()
        description = os.path.join(model_dir, config.MODEL_DESCRIPTION_FILENAME)
        with open(description, "w") as description_file:
            description_file.write("from yimt.models import catalog\n")
            description_file.write("model = catalog.Transformer\n")
        model = config.load_model(model_dir)
        self.assertIsInstance(model, Model)

    def testLoadModelFile(self):
        model_file = self._writeCustomModel()
        model_dir = self.get_temp_dir()
        model = config.load_model(model_dir, model_file=model_file)
        saved_description_path = os.path.join(
            model_dir, config.MODEL_DESCRIPTION_FILENAME
        )
        self.assertTrue(os.path.exists(saved_description_path))
        self.assertTrue(filecmp.cmp(model_file, saved_description_path))
        self.assertEqual(model, 42)
        model = config.load_model(model_dir)
        self.assertEqual(model, 42)

    def testLoadModelFileOverride(self):
        model_dir = self.get_temp_dir()
        saved_description_path = os.path.join(
            model_dir, config.MODEL_DESCRIPTION_FILENAME
        )
        model_file = self._writeCustomModel(filename="test_model1.py", return_value=1)
        config.load_model(model_dir, model_file=model_file)
        self.assertTrue(filecmp.cmp(model_file, saved_description_path))
        model_file = self._writeCustomModel(filename="test_model2.py", return_value=2)
        config.load_model(model_dir, model_file=model_file)
        self.assertTrue(filecmp.cmp(model_file, saved_description_path))

    def testLoadModelInvalidArguments(self):
        with self.assertRaises(ValueError):
            config.load_model(self.get_temp_dir(), model_file="a", model_name="b")

    def testLoadModelInvalidInvalidName(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            config.load_model(self.get_temp_dir(), model_name="b")

    def testLoadModelInvalidInvalidFile(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            config.load_model(self.get_temp_dir(), model_file="a")

    def testLoadModelMissingModel(self):
        with self.assertRaises(RuntimeError):
            config.load_model(self.get_temp_dir())

    def testPathsPrefix(self):
        a = os.path.join(self.get_temp_dir(), "a.txt")
        b = os.path.join(self.get_temp_dir(), "b.txt")
        open(a, "w").close()
        open(b, "w").close()

        original_config = {
            "a": "a.txt",
            "b": ["b.txt"],
            "c": {"a": "a.txt", "d": "d.txt"},
        }
        expected_config = {
            "a": a,
            "b": [b],
            "c": {"a": a, "d": "d.txt"},
        }

        self.assertDictEqual(
            config.try_prefix_paths(self.get_temp_dir(), original_config),
            expected_config,
        )


if __name__ == "__main__":
    tf.test.main()
