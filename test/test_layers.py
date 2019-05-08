import torch

from horch import cuda
from horch.nn.psroi_align import PSRoIAlign
from horch.detection import BBox


def test_psroi_align():
    spatial_scale = 1/64
    out_channels = 2
    pooled_width = 2
    pooled_height = 2
    output_size = (pooled_width, pooled_height)
    sampling_ratio = 2
    l = PSRoIAlign(out_channels, output_size, spatial_scale,
                   sampling_ratio=sampling_ratio)
    input = torch.tensor([[
        # (c, w, h)
        # (0, 0, 0)
        [[0.3386, 0.2903, 0.3211, 0.8799, 0.6430],
         [0.9942, 0.6858, 0.4229, 0.8161, 0.0372],
         [0.4667, 0.3435, 0.2200, 0.7059, 0.4643],
         [0.3431, 0.2514, 0.2474, 0.1668, 0.9396],
         [0.7272, 0.3062, 0.0667, 0.0015, 0.2331]],
        # (0, 0, 1)
        [[0.3743, 0.6907, 0.3557, 0.3587, 0.8099],
         [0.6510, 0.3498, 0.4020, 0.7310, 0.4720],
         [0.3433, 0.0828, 0.1647, 0.1137, 0.1935],
         [0.3943, 0.3530, 0.5282, 0.1910, 0.3444],
         [0.5046, 0.5505, 0.1741, 0.5111, 0.4039]],
        # (0, 1, 0)
        [[0.7212, 0.7331, 0.4281, 0.5474, 0.0612],
         [0.2318, 0.8664, 0.3478, 0.9044, 0.5250],
         [0.9788, 0.2954, 0.5962, 0.6162, 0.9372],
         [0.4921, 0.8632, 0.7297, 0.2732, 0.1844],
         [0.6264, 0.7785, 0.7025, 0.0687, 0.5185]],
        # (0, 1, 1)
        [[0.1258, 0.5941, 0.4474, 0.3031, 0.8499],
         [0.6679, 0.6695, 0.2245, 0.0476, 0.6717],
         [0.8167, 0.6604, 0.5939, 0.6296, 0.7218],
         [0.8974, 0.7918, 0.3926, 0.9738, 0.8589],
         [0.1273, 0.5575, 0.4166, 0.4341, 0.2427]],

        [[0.1450, 0.0391, 0.7799, 0.8656, 0.6891],
         [0.1404, 0.1151, 0.5571, 0.1208, 0.4987],
         [0.5341, 0.8148, 0.8216, 0.7567, 0.9848],
         [0.1533, 0.3924, 0.3584, 0.9173, 0.9549],
         [0.2370, 0.3540, 0.4390, 0.4546, 0.7849]],

        [[0.0751, 0.9223, 0.4721, 0.3994, 0.5512],
         [0.2268, 0.8096, 0.4849, 0.5522, 0.1864],
         [0.6405, 0.0099, 0.0845, 0.8138, 0.5590],
         [0.1224, 0.2964, 0.9686, 0.4867, 0.9724],
         [0.1677, 0.5063, 0.3987, 0.1951, 0.9811]],

        [[0.3705, 0.6998, 0.8598, 0.3607, 0.1545],
         [0.2398, 0.9740, 0.6375, 0.0643, 0.0624],
         [0.7160, 0.8220, 0.4669, 0.5930, 0.0680],
         [0.3281, 0.5764, 0.7522, 0.8315, 0.6307],
         [0.6143, 0.3002, 0.0761, 0.3627, 0.3021]],

        [[0.5256, 0.4123, 0.0614, 0.8413, 0.0322],
         [0.0296, 0.4799, 0.1590, 0.8119, 0.7496],
         [0.4775, 0.9796, 0.8784, 0.5922, 0.4398],
         [0.0339, 0.8859, 0.6292, 0.7069, 0.5664],
         [0.6811, 0.5400, 0.4801, 0.2457, 0.9451]]]], requires_grad=True)
    roi = torch.tensor([[0, 30.5481,  49.9075, 168.1317, 248.5454]])
    out = l(input, roi)
    out.sum().backward()


def test_psroi_align_cuda():

    out_channels = 2
    pooled_width = 3
    pooled_height = 3
    output_size = (pooled_width, pooled_height)
    sampling_ratio = 2
    l = PSRoIAlign(out_channels, output_size,
                   sampling_ratio=sampling_ratio, adaptive=True)
    x = torch.randn(2, out_channels * pooled_height * pooled_width, 7, 5)
    roi = BBox.convert(torch.rand(6, 4), BBox.XYWH, BBox.LTRB)
    indices = torch.tensor([0, 0, 0, 1, 1, 1.]).view(6, 1)
    roi = torch.cat([indices, roi], dim=1)
    res = l(x, roi)
    res_cuda = l(cuda(x), cuda(roi))
    diff = res - res_cuda.cpu()
    assert diff.mean() < 1e-8
