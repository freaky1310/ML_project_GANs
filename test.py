import torch
import torchvision.transforms as transforms
import torch.nn as nn
import numpy as np
import os
import math

from torch import FloatTensor
from PIL import Image

from nets import FCNN
from utils import crop_central_square

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
    # PSNR from review
    psnr = 10 * math.log10((255**2) / loss.item())
    # PSNR from tensorflow source code
    #psnr = 20 * math.log(255) / math.log(10.0) - np.float32(10 / np.log(10)) * math.log(loss)

    trans = transforms.ToPILImage(mode='RGB')
    output = output.view((3, 256, 256))
    output = trans(output)
    output.show(title="Guessing")
    print('PSNR score for test image {x} is: %f'.format(x=image_name) % psnr)
    return psnr


if __name__ == '__main__':

    """net = FCNN(input_channels=3)
    net.load_state_dict(torch.load('state_10e_pil.pth', map_location=torch.device('cpu')))
    net.eval()
    avg_psnr = 0
    for image_name in os.listdir('evaluation/Set5/lr'):
        img = Image.open('evaluation/Set5/lr/{x}'.format(x=image_name))
        target = Image.open('evaluation/Set5/hr/{x}'.format(x=image_name))
        avg_psnr += test_single(net, 'evaluation/Set5/', image_name, criterion=nn.MSELoss(reduction='mean'))
        #img.show(title="Input")
        target.show(title="Target")
    avg_psnr = avg_psnr / len(os.listdir('evaluation/Set5/lr'))
    print('Average psnr score is: %f' % avg_psnr)"""
    scale_factor = 4
    pilimg = transforms.ToPILImage()
    tens = transforms.ToTensor()
    x = Image.open('house.png')
    x = crop_central_square(x)
    y = x.resize((256, 256))
    x = x.resize((64, 64))

    net = FCNN()
    net.load_state_dict(torch.load('state_10e_pil.pth', map_location=torch.device('cpu')))
    net.eval()

    input = tens(x)
    input = input.view((1, 3, 64, 64))

    target = net(input)

    residual = x.resize((x.size[0] * scale_factor, x.size[1] * scale_factor),
                        Image.BICUBIC)

    out = target - tens(residual)
    target = pilimg(target.view((3, 256, 256)))
    out = pilimg(out.view((3, 256, 256)))
    target.show()
    out.show()
    residual.show()



