import torchvision.transforms as transforms
import os, random
import numpy as np
import torch
import matplotlib.pyplot as plt

from torch.utils.data import Dataset
from PIL import Image, PngImagePlugin
from skimage import io
from skimage.transform import resize

from utils import random_crop, custom_bicubic

class COCO(Dataset):

    def __init__(self, image_paths, target_paths, scale_factor=4, patch_size=32):   # initial logic happens like transform

        self.image_paths = image_paths
        self.target_paths = target_paths
        self.transforms = transforms.ToTensor()
        self.scale_factor = scale_factor
        self.patch_size = patch_size
        self.upsample_size = self.patch_size * self.scale_factor
        self.train_imgs = os.listdir(self.image_paths)
        self.transforms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.47614917, 0.45001204, 0.40904046], std=[0.229, 0.224, 0.225])])

        PngImagePlugin.MAX_TEXT_CHUNK = 1000 * (1024 ** 2)

    def __getitem__(self, index):

        image = io.imread(self.image_paths + self.train_imgs[index])
        target = io.imread(self.target_paths + self.train_imgs[index])
        bicub = resize(image, (self.upsample_size, self.upsample_size))

        image = np.array(image, dtype=np.float64) / 255
        target = np.array(target, dtype=np.float64) / 255

        """image = np.swapaxes(image, 2, 1)
        target = np.swapaxes(target, 2, 1)
        bicub = np.swapaxes(bicub, 2, 1)
        image = np.swapaxes(image, 1, 0)
        target = np.swapaxes(target, 1, 0)
        bicub = np.swapaxes(bicub, 1, 0)"""

        return self.transforms(image), target, bicub

    def __len__(self):  # return count of sample we have

        return len(self.train_imgs)
