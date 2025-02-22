
import sys
sys.path.append('E:\pythonwork\caffe\python')
import caffe

import ipdb
import cv2
import numpy as np
import skimage

deploy = 'E:\pythonwork\caffe\models\VGG\VGG_ILSVRC_19_layers_deploy.prototxt'
model = 'E:\pythonwork\caffe\models\VGG\VGG_ILSVRC_19_layers.caffemodel'
mean = 'E:\pythonwork\caffe\python\caffe\imagenet/ilsvrc_2012_mean.npy'

class CNN(object):

    def __init__(self, deploy=deploy, model=model, mean=mean, batch_size=50, width=227, height=227):

        self.deploy = deploy
        self.model = model
        self.mean = mean

        self.batch_size = batch_size
        self.net, self.transformer = self.get_net()
        self.net.blobs['data'].reshape(self.batch_size, 3, height, width)

        self.width = width
        self.height = height

    def get_net(self):
        caffe.set_mode_gpu()
        net = caffe.Net(self.deploy, self.model, caffe.TEST)

        transformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2,0,1))
        transformer.set_mean('data', np.load(self.mean).mean(1).mean(1))
        transformer.set_raw_scale('data', 255)
        transformer.set_channel_swap('data', (2,1,0))

        return net, transformer

    def get_features(self, image_list, layers='fc7', layer_sizes=[4096]):
        print(image_list)
        #image_list = list(image_list)
        iter_until = len(image_list) + self.batch_size
        # we fill the zeros 
        #num_frames = 80
        #all_feats = np.zeros([num_frames] + layer_sizes)
        all_feats = np.zeros([len(image_list)] + layer_sizes)

        for start, end in zip(range(0, iter_until, self.batch_size), \
                              range(self.batch_size, iter_until, self.batch_size)):

            image_batch = image_list[start:end]

            caffe_in = np.zeros(np.array(image_batch.shape)[[0,3,1,2]], dtype=np.float32)

            for idx, in_ in enumerate(image_batch):
                caffe_in[idx] = self.transformer.preprocess('data', in_)

            out = self.net.forward_all(blobs=[layers], **{'data':caffe_in})
            feats = out[layers]

            all_feats[start:end] = feats

        return all_feats

