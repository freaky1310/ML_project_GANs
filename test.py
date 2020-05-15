import torch
import torchvision.transforms as transforms
import torch.nn as nn
import numpy as np
import os
import math

from torch import FloatTensor
from PIL import Image

from nets import FCNN

def test_single(net, image_folder, image_name, criterion):
    net.eval()
    img = Image.open(image_folder + 'lr/' + image_name)
    target = Image.open(image_folder + 'hr/' + image_name)
    tens = transforms.ToTensor()

    target = tens(target)
    target = target.view((1, 3, 256, 256))
    input = tens(img)

    input = input.view((1, 3, 64, 64))
    output = net(input)

    loss = criterion(output, target)
    psnr = 10 * math.log10(1 / loss.item())

    trans = transforms.ToPILImage(mode='RGB')
    output = output.view((3, 256, 256))
    output = trans(output)
    #output.show(title="Guessing")
    print('PSNR score for test image {x} is: %f'.format(x=image_name) % psnr)
    return psnr


if __name__ == '__main__':

    net = FCNN(input_channels=3)
    avg_psnr = 0
    for image_name in os.listdir('evaluation/Set14/lr'):
        img = Image.open('evaluation/Set14/lr/{x}'.format(x=image_name))
        target = Image.open('evaluation/Set14/hr/{x}'.format(x=image_name))
        net.load_state_dict(torch.load('state_10e.pth', map_location=torch.device('cpu')))
        avg_psnr += test_single(net, 'evaluation/Set14/', image_name, criterion=nn.MSELoss())
        #img.show(title="Input")
        #target.show(title="Target")
    avg_psnr = avg_psnr / len(os.listdir('evaluation/Set14/lr'))
    print('Average psnr score is: %f' % avg_psnr)


