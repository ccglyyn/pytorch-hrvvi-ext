import torch
import torch.nn as nn
import torch.nn.functional as F

from hutil.model.modules import Conv2d, get_norm_layer
from hutil.model.utils import get_out_channels, get_loc_cls_preds


def depthwise_seperable_conv3x3(in_channels, out_channels, stride=1, padding=1):
    return nn.Sequential(
        Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, padding=padding, groups=in_channels,
               norm_layer='gn'),
        Conv2d(in_channels, out_channels, kernel_size=1),
    )


class DownBlock(nn.Module):
    def __init__(self, in_channels, out_channels, padding=1):
        super().__init__()
        channels = out_channels // 2
        self.conv1 = Conv2d(in_channels, channels, kernel_size=1,
                            norm_layer='gn', activation='relu')
        self.conv2 = depthwise_seperable_conv3x3(
            channels, out_channels, stride=2, padding=padding)
        self.gn2 = get_norm_layer('gn', out_channels)
        self.relu2 = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.gn2(x)
        x = self.relu2(x)
        return x


class SSDLite(nn.Module):
    def __init__(self, backbone, num_anchors=(6, 6, 6, 6, 4), num_classes=21, f_channels=256, pad_last=False):
        super().__init__()
        self.num_classes = num_classes
        # self.backbone = MobileNetV2()
        self.backbone = backbone
        self.with_stride8 = 3 in backbone.feature_levels
        num_anchors = tuple(num_anchors)
        backbone_channels = self.backbone.out_channels

        if self.with_stride8:
            self.pred3 = depthwise_seperable_conv3x3(
                backbone_channels[-3], num_anchors[0] * (4 + num_classes))
        else:
            num_anchors = (0,) + num_anchors
        self.pred4 = depthwise_seperable_conv3x3(
            backbone_channels[-2], num_anchors[1] * (4 + num_classes))
        self.pred5 = depthwise_seperable_conv3x3(
            backbone_channels[-1], num_anchors[2] * (4 + num_classes))

        if len(num_anchors) > 3:
            self.layer6 = DownBlock(
                backbone_channels[-1], 2 * f_channels)
            self.pred6 = depthwise_seperable_conv3x3(
                get_out_channels(self.layer6), num_anchors[3] * (4 + num_classes))
        if len(num_anchors) > 4:
            self.layer7 = DownBlock(2 * f_channels, f_channels)
            self.pred7 = depthwise_seperable_conv3x3(
                get_out_channels(self.layer7), num_anchors[4] * (4 + num_classes))
        if len(num_anchors) > 5:
            padding = 1 if pad_last else 0
            self.layer8 = DownBlock(f_channels, f_channels, padding=padding)
            self.pred8 = depthwise_seperable_conv3x3(
                get_out_channels(self.layer8), num_anchors[5] * (4 + num_classes))

        self.num_anchors = num_anchors

    def forward(self, x):
        if self.with_stride8:
            c3, c4, c5 = self.backbone(x)
        else:
            c4, c5 = self.backbone(x)

        p4 = self.pred4(c4)
        p5 = self.pred5(c5)
        ps = [p4, p5]
        if self.with_stride8:
            p3 = self.pred3(c3)
            ps = [p3] + ps
        if len(self.num_anchors) > 3:
            c6 = self.layer6(c5)
            p6 = self.pred6(c6)
            ps.append(p6)
        if len(self.num_anchors) > 4:
            c7 = self.layer7(c6)
            p7 = self.pred7(c7)
            ps.append(p7)
        if len(self.num_anchors) > 5:
            c8 = self.layer8(c7)
            p8 = self.pred8(c8)
            ps.append(p8)

        loc_p, cls_p = get_loc_cls_preds(ps, self.num_classes)
        return loc_p, cls_p