# Lint as: python3
# Copyright 2019, The TensorFlow Federated Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections

from absl.testing import absltest
import numpy as np
import tensorflow as tf

from tensorflow_federated.python.simulation.datasets import emnist


class LoadDataTest(tf.test.TestCase, absltest.TestCase):

  def test_synthetic(self):
    client_data = emnist.get_synthetic(num_clients=4)
    self.assertLen(client_data.client_ids, 4)

    self.assertEqual(
        client_data.element_type_structure,
        collections.OrderedDict([
            ('pixels', tf.TensorSpec(shape=(28, 28), dtype=tf.float32)),
            ('label', tf.TensorSpec(shape=(), dtype=tf.int32)),
        ]))

    for client_id in client_data.client_ids:
      data = self.evaluate(
          list(client_data.create_tf_dataset_for_client(client_id)))
      images = [x['pixels'] for x in data]
      labels = [x['label'] for x in data]
      self.assertLen(labels, 10)
      self.assertCountEqual(labels, list(range(10)))
      self.assertLen(images, 10)
      self.assertEqual(images[0].shape, (28, 28))
      self.assertEqual(images[-1].shape, (28, 28))

  def test_infinite_transformed_data_doesnt_change(self):
    # The point of this test is to validate that the images generated by
    # emnist.get_infinite() are always the same.  (They are pseudorandom, but
    # random seed should always be the same, so that outputs are consistent.)
    raw_client_data = emnist.get_synthetic(num_clients=1)
    inf_client_data = emnist.get_infinite(raw_client_data, num_pseudo_clients=2)

    # Generate the dataset for one of the 'infinite' clients. (I.e., one of the
    # clients that is formed by random translations, shearing, etc.).
    inf_dataset = inf_client_data.create_tf_dataset_for_client(
        inf_client_data.client_ids[-1])
    inf_dataset_iter = iter(inf_dataset)
    img0_from_inf_dataset = next(inf_dataset_iter)['pixels']
    img1_from_inf_dataset = next(inf_dataset_iter)['pixels']
    img2_from_inf_dataset = next(inf_dataset_iter)['pixels']

    # Just take the first few images from the 'infinite' client's dataset, and
    # check that the average of the pixel values never changes.
    self.assertAlmostEqual(np.average(img0_from_inf_dataset), 0.8107493)
    self.assertAlmostEqual(np.average(img1_from_inf_dataset), 0.8532163)
    self.assertAlmostEqual(np.average(img2_from_inf_dataset), 0.8392606)


if __name__ == '__main__':
  tf.compat.v1.enable_v2_behavior()
  tf.test.main()
