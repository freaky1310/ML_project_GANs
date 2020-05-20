import torchvision.transforms as transforms

from torch import nn
from collections import OrderedDict
from PIL import Image


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.in_channels, self.out_channels = in_channels, out_channels
        self.block1 = nn.Sequential(OrderedDict([
            ('c1', nn.Conv2d(64, 64, kernel_size=(3, 3), padding=(1, 1))),
            ('relu1', nn.ReLU()),
            ]))
        self.block2 = nn.Conv2d(64, 64, kernel_size=(3, 3), padding=(1, 1))


    def forward(self, x):
        residual = x
        x = self.block1(x)
        x = self.block2(x)
        x += residual
        return x


class FCNN(nn.Module):

    def __init__(self, input_channels=3, scale_factor=4):
        super().__init__()
        self.input_channels = input_channels
        self.bicubic_upsample = nn.Upsample(scale_factor=4, mode='bicubic')
        self.tens = transforms.ToTensor()
        self.pilimg = transforms.ToPILImage()
        self.scale_factor = scale_factor

        self.conv1 = nn.Sequential(OrderedDict([
            ('c1', nn.Conv2d(self.input_channels, 64, kernel_size=(3, 3), padding=(1, 1))),
            ('relu1', nn.ReLU())
        ]))
        self.residual = nn.Sequential(OrderedDict([
            ('res1', ResidualBlock(64, 64)),
            ('res2', ResidualBlock(64, 64)),
            ('res3', ResidualBlock(64, 64)),
            ('res4', ResidualBlock(64, 64)),
            ('res5', ResidualBlock(64, 64)),
            ('res6', ResidualBlock(64, 64)),
            ('res7', ResidualBlock(64, 64)),
            ('res8', ResidualBlock(64, 64)),
            ('res9', ResidualBlock(64, 64)),
            ('res10', ResidualBlock(64, 64))
        ]))
        self.upsamp1 = nn.Sequential(OrderedDict([
            ('up1ctrans', nn.UpsamplingNearest2d(scale_factor=2)),
            ('up1conv', nn.Conv2d(64, 64, kernel_size=(3, 3), padding=(1, 1))),
            ('up1relu', nn.ReLU())
        ]))
        self.upsamp2 = nn.Sequential(OrderedDict([
            ('up2ctrans', nn.UpsamplingNearest2d(scale_factor=2)),
            ('up2conv', nn.Conv2d(64, 64, kernel_size=(3, 3), padding=(1, 1))),
            ('up2relu', nn.ReLU())
        ]))
        self.conv2 = nn.Sequential(OrderedDict([
            ('c2', nn.Conv2d(64, 64, kernel_size=(3, 3), padding=(1, 1))),
            ('relu2', nn.ReLU())
        ]))
        self.conv3 = nn.Sequential(OrderedDict([
            ('c3', nn.Conv2d(64, 3, kernel_size=(3, 3), padding=(1, 1)))
        ]))

    def forward(self, x):
        w = x.shape[2]
        h = x.shape[3]
        y = self.conv1(x)
        y = self.residual(y)
        y = self.upsamp1(y)
        y = self.upsamp2(y)
        y = self.conv2(y)
        y = self.conv3(y)
        x = x.view((3, w, h))
        residual = self.pilimg(x.cpu())
        residual = residual.resize((residual.size[0] * self.scale_factor, residual.size[1] * self.scale_factor),
                                   Image.BICUBIC)
        residual = self.tens(residual)
        return y + residual.cuda()
