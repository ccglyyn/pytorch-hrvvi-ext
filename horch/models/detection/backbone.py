from difflib import get_close_matches

import torch.nn as nn

from pytorchcv.model_provider import get_model as ptcv_get_model

from horch.models.mobilenet import mobilenetv2
from horch.models.mobilenetv3 import mobilenetv3
from horch.models.snet import SNet as BSNet
from horch.models.utils import get_out_channels, calc_out_channels
from horch.models.darknet import Darknet as BDarknet


class ShuffleNetV2(nn.Module):
    mult2name = {
        0.5: "shufflenetv2_wd2",
        1.0: "shufflenetv2_w1",
        1.5: "shufflenetv2_w3d2",
        2.0: "shufflenetv2_w2",
    }
    r"""ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design

    Parameters
    ----------
    mult: float
        Width multiplier which could one of [ 0.5, 1.0, 1.5, 2.0 ]
        Default: 0.5
    feature_levels : sequence of int
        Feature levels to output.
        Default: (3, 4, 5)
    """

    def __init__(self, mult=1.0, feature_levels=(3, 4, 5), pretrained=False, **kwargs):
        super().__init__()
        self.feature_levels = feature_levels
        if pretrained:
            norm_layer = kwargs.get("norm_layer")
            assert norm_layer is None or norm_layer == 'bn', "`gn` can be only set when `pretrained` is False"
            net = ptcv_get_model(self.mult2name[mult], pretrained=True)
            del net.output
            net = net.features
            self.layer1 = net.init_block.conv
            self.layer2 = net.init_block.pool
            self.layer3 = net.stage1
            self.layer4 = net.stage2
            self.layer5 = nn.Sequential(
                net.stage3,
                net.final_block,
            )
            out_channels = [
                get_out_channels(self.layer1),
                get_out_channels(self.layer1),
                calc_out_channels(self.layer3),
                calc_out_channels(self.layer4),
                calc_out_channels(self.layer5),
            ]
        else:
            from horch.models.re.shufflenet import shufflenet_v2 as BShuffleNetV2
            net = BShuffleNetV2(mult=mult, **kwargs)
            channels = net.out_channels
            del net.fc
            self.layer1 = net.conv1
            self.layer2 = net.maxpool
            self.layer3 = net.stage2
            self.layer4 = net.stage3
            self.layer5 = nn.Sequential(
                net.stage4,
                net.conv5,
            )
            out_channels = [channels[0]] + channels[:3] + [channels[-1]]
        self.out_channels = [
            out_channels[i - 1] for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


class SNet(nn.Module):
    r"""ThunderNet: Towards Real-time Generic Object Detection

    Args:
        version (int): 49, 146, 535
            Default: 49
        feature_levels (sequence of int): features of which layers to output
            Default: (3, 4, 5)
    """

    def __init__(self, version=49, feature_levels=(3, 4, 5), **kwargs):
        super().__init__()
        net = BSNet(num_classes=1, version=version, **kwargs)
        del net.fc
        channels = net.channels
        self.layer1 = net.conv1
        self.layer2 = net.maxpool
        self.layer3 = net.stage2
        self.layer4 = net.stage3
        if len(channels) == 5:
            self.layer5 = nn.Sequential(
                net.stage4,
                net.conv5,
            )
        else:
            self.layer5 = net.stage4
        out_channels = [channels[0]] + channels[:3] + [channels[-1]]
        self.feature_levels = feature_levels
        self.out_channels = [
            out_channels[i - 1] for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return tuple(outs)


# class ResNet(nn.Module):
#     r"""Pretrained ResNet from torchvision
#
#     Args:
#         version (int): 18, 50, 101
#             Default: 18
#         feature_levels (list of int): features of which layers to output
#             Default: (3, 4, 5)
#     """
#
#     def __init__(self, version=18, feature_levels=(3, 4, 5)):
#         super().__init__()
#         if version == 18:
#             net = resnet18(pretrained=True)
#         elif version == 50:
#             net = resnet50(pretrained=True)
#         elif version == 101:
#             net = resnet101(pretrained=True)
#         else:
#             raise ValueError("version must be one of [18, 50, 101]")
#         del net.fc
#         self.layer1 = nn.Sequential(
#             net.conv1,
#             net.bn1,
#             net.relu,
#         )
#         self.layer2 = net.maxpool
#         self.layer3 = nn.Sequential(
#             net.layer1,
#             net.layer2,
#         )
#         self.layer4 = net.layer3
#         self.layer5 = net.layer4
#         out_channels = [
#             64, 64,
#             get_out_channels(self.layer3),
#             get_out_channels(self.layer4),
#             get_out_channels(self.layer5),
#         ]
#         self.feature_levels = feature_levels
#         self.out_channels = [
#             out_channels[i - 1] for i in feature_levels
#         ]
#
#     def forward(self, x):
#         outs = []
#         x = self.layer1(x)
#         x = self.layer2(x)
#         if 2 in self.feature_levels:
#             outs.append(x)
#         x = self.layer3(x)
#         if 3 in self.feature_levels:
#             outs.append(x)
#         x = self.layer4(x)
#         if 4 in self.feature_levels:
#             outs.append(x)
#         x = self.layer5(x)
#         if 5 in self.feature_levels:
#             outs.append(x)
#         return outs


class MobileNetV2(nn.Module):
    r"""MobileNetV2: Inverted Residuals and Linear Bottlenecks

    Args:
        feature_levels (list of int): features of which layers to output
            Default: (3, 4, 5)
    """

    mult2name = {
        0.25: "mobilenetv2_wd4",
        0.5: "mobilenetv2_wd2",
        0.75: "mobilenetv2_w3d4",
        1.0: "mobilenetv2_w1",
    }

    def __init__(self, mult=1.0, feature_levels=(3, 4, 5), pretrained=True, **kwargs):
        super().__init__()
        self.feature_levels = feature_levels
        if pretrained:
            norm_layer = kwargs.get("norm_layer")
            assert norm_layer is None or norm_layer == 'bn', "`gn` can be only set when `pretrained` is False"
            net = ptcv_get_model(self.mult2name[mult], pretrained=True)
            del net.output
            net = net.features
            self.layer1 = nn.Sequential(
                net.init_block,
                net.stage1,
                net.stage2.unit1.conv1,
            )
            self.layer2 = nn.Sequential(
                net.stage2.unit1.conv2,
                net.stage2.unit1.conv3,
                net.stage2.unit2,
                net.stage3.unit1.conv1,
            )
            self.layer3 = nn.Sequential(
                net.stage3.unit1.conv2,
                net.stage3.unit1.conv3,
                *net.stage3[1:],
                net.stage4.unit1.conv1,
            )
            self.layer4 = nn.Sequential(
                net.stage4.unit1.conv2,
                net.stage4.unit1.conv3,
                *net.stage4[1:],
                net.stage5.unit1.conv1,
            )
            self.layer5 = nn.Sequential(
                net.stage5.unit1.conv2,
                net.stage5.unit1.conv3,
                *net.stage5[1:],
                net.final_block,
            )
        else:
            backbone = mobilenetv2(mult=mult, pretrained=pretrained)
            del backbone.classifier
            features = backbone.features

            self.layer1 = features[:2]
            self.layer2 = features[2:4]
            self.layer3 = nn.Sequential(
                *features[4:7],
                features[7].conv[:3],
            )
            self.layer4 = nn.Sequential(
                features[7].conv[3:],
                *features[8:14],
                features[14].conv[:3],
            )
            self.layer5 = nn.Sequential(
                features[14].conv[3:],
                *features[15:],
                backbone.conv,
            )
        self.out_channels = [
            get_out_channels(getattr(self, ("layer%d" % i)))
            for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


class MobileNetV3(nn.Module):
    r"""MobileNetV3: Searching for MobileNetV3

    Args:
        feature_levels (list of int): features of which layers to output
            Default: (3, 4, 5)
    """

    def __init__(self, mult=1.0, feature_levels=(3, 4, 5), pretrained=False, norm_layer='bn'):
        super().__init__()
        assert not pretrained, "Pretrained models are not avaliable now."
        backbone = mobilenetv3(mult=mult, num_classes=1, norm_layer=norm_layer)
        del backbone.classifier
        features = backbone.features

        self.layer1 = features[:2]
        self.layer2 = features[2:4]
        self.layer3 = nn.Sequential(
            *features[4:7],
            features[7].conv[:3],
        )
        self.layer4 = nn.Sequential(
            features[7].conv[3:],
            *features[8:14],
            features[14].conv[:3],
        )
        self.layer5 = nn.Sequential(
            features[14].conv[3:],
            *features[15:],
        )
        self.feature_levels = feature_levels
        self.out_channels = [
            get_out_channels(getattr(self, ("layer%d" % i)))
            for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


class SqueezeNet(nn.Module):
    r"""SqueezeNet: AlexNet-level accuracy with 50x fewer parameters and <0.5MB models size

    Args:
        feature_levels (list of int): features of which layers to output
            Default: (3, 4, 5)
    """

    def __init__(self, feature_levels=(3, 4, 5)):
        super().__init__()
        from torchvision.models.squeezenet import squeezenet1_1, Fire
        backbone = squeezenet1_1(pretrained=True)
        del backbone.classifier
        backbone = backbone.features
        backbone[0].padding = (1, 1)

        self.layer1 = backbone[:2]
        self.layer2 = backbone[2:5]
        self.layer3 = backbone[5:8]
        self.layer4 = backbone[8:]

        if 5 in feature_levels:
            self.layer5 = nn.Sequential(
                nn.MaxPool2d(kernel_size=3, stride=2, ceil_mode=True),
                Fire(512, 64, 256, 256),
            )

        channels = [64, 128, 256, 512, 512]

        self.feature_levels = feature_levels
        self.out_channels = [
            channels[i - 1] for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        if 5 in self.feature_levels:
            x = self.layer5(x)
            outs.append(x)
        return outs


class Darknet(nn.Module):
    def __init__(self, feature_levels=(3, 4, 5), pretrained=False, **kwargs):
        super().__init__()
        self.feature_levels = feature_levels
        if pretrained:
            norm_layer = kwargs.get("norm_layer")
            assert norm_layer is None or norm_layer == 'bn', "`gn` can be only set when `pretrained` is False"
            net = ptcv_get_model("darknet53", pretrained=True)
            del net.output
            net = net.features
            self.layer1 = nn.Sequential(
                net.init_block,
                net.stage1,
            )
            self.layer2 = net.stage2
            self.layer3 = net.stage3
            self.layer4 = net.stage4
            self.layer5 = net.stage5
        else:
            backbone = BDarknet(num_classes=1, **kwargs)
            del backbone.fc
            self.layer1 = nn.Sequential(
                backbone.conv0,
                backbone.down1,
                backbone.layer1,
            )

            self.layer2 = nn.Sequential(
                backbone.down2,
                backbone.layer2,
            )

            self.layer3 = nn.Sequential(
                backbone.down3,
                backbone.layer3,
            )

            self.layer4 = nn.Sequential(
                backbone.down4,
                backbone.layer4,
            )

            self.layer5 = nn.Sequential(
                backbone.down5,
                backbone.layer5,
            )
        self.out_channels = [
            get_out_channels(getattr(self, ("layer%d" % i)))
            for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


class ResNet(nn.Module):
    def __init__(self, name, feature_levels=(3, 4, 5), pretrained=True):
        super().__init__()
        self.feature_levels = feature_levels
        net = ptcv_get_model(name, pretrained=pretrained)
        del net.output
        net = net.features
        self.layer1 = net.init_block.conv
        self.layer2 = nn.Sequential(
            net.init_block.pool,
            net.stage1,
        )
        self.layer3 = net.stage2
        self.layer4 = net.stage3
        if hasattr(net, "post_activ"):
            self.layer5 = nn.Sequential(
                net.stage4,
                net.post_activ,
            )
        else:
            self.layer5 = nn.Sequential(
                net.stage4,
            )
        self.out_channels = [
            calc_out_channels(getattr(self, ("layer%d" % i)))
            for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


class Backbone(nn.Module):
    def __init__(self, name, feature_levels=(3, 4, 5), pretrained=True):
        super().__init__()
        self.feature_levels = feature_levels
        net = ptcv_get_model(name, pretrained=pretrained)
        del net.output
        net = net.features
        self.layer1 = net.init_block.conv
        self.layer2 = nn.Sequential(
            net.init_block.pool,
            net.stage1,
        )
        self.layer3 = net.stage2
        self.layer4 = net.stage3
        if hasattr(net, "post_activ"):
            self.layer5 = nn.Sequential(
                net.stage4,
                net.post_activ,
            )
        else:
            self.layer5 = nn.Sequential(
                net.stage4,
            )
        self.out_channels = [
            calc_out_channels(getattr(self, ("layer%d" % i)))
            for i in feature_levels
        ]

    def forward(self, x):
        outs = []
        x = self.layer1(x)
        x = self.layer2(x)
        if 2 in self.feature_levels:
            outs.append(x)
        x = self.layer3(x)
        if 3 in self.feature_levels:
            outs.append(x)
        x = self.layer4(x)
        if 4 in self.feature_levels:
            outs.append(x)
        x = self.layer5(x)
        if 5 in self.feature_levels:
            outs.append(x)
        return outs


def search(name, n=10):
    from pytorchcv.models.model_store import _model_sha1
    models = _model_sha1.keys()
    return get_close_matches(models, name, n=n)