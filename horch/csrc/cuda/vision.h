#pragma once
#include <torch/extension.h>

at::Tensor PSROIAlign_forward_cuda(const at::Tensor &input,
                                   const at::Tensor &rois, const float scale_h,
                                   const float scale_w, const int out_channels,
                                   const int pooled_height,
                                   const int pooled_width,
                                   const int sampling_ratio);

at::Tensor PSROIAlign_backward_cuda(
    const at::Tensor &grad, const at::Tensor &rois, const float scale_h,
    const float scale_w, const int out_channels, const int pooled_height,
    const int pooled_width, const int batch_size, const int channels,
    const int height, const int width, const int sampling_ratio);

at::Tensor iou_mn_forward_cuda(const at::Tensor &boxes1,
                               const at::Tensor &boxes2);

std::tuple<at::Tensor, at::Tensor>
iou_mn_backward_cuda(const at::Tensor &dout, const at::Tensor &boxes1,
                     const at::Tensor &boxes2, const at::Tensor &ious);

at::Tensor ROIAlign_forward_cuda(const at::Tensor &input,
                                 const at::Tensor &rois, const float scale_h,
                                 const float scale_w, const int pooled_height,
                                 const int pooled_width,
                                 const int sampling_ratio);

at::Tensor ROIAlign_backward_cuda(const at::Tensor &grad,
                                  const at::Tensor &rois, const float scale_h,
                                  const float scale_w, const int pooled_height,
                                  const int pooled_width, const int batch_size,
                                  const int channels, const int height,
                                  const int width, const int sampling_ratio);

at::Tensor nms_cuda(const at::Tensor boxes, float nms_overlap_thresh);

void deformable_im2col(const at::Tensor data_im, const at::Tensor data_offset,
                       const int channels, const int height, const int width,
                       const int ksize_h, const int ksize_w, const int pad_h,
                       const int pad_w, const int stride_h, const int stride_w,
                       const int dilation_h, const int dilation_w,
                       const int parallel_imgs, const int deformable_group,
                       at::Tensor data_col);

void deformable_col2im(const at::Tensor data_col, const at::Tensor data_offset,
                       const int channels, const int height, const int width,
                       const int ksize_h, const int ksize_w, const int pad_h,
                       const int pad_w, const int stride_h, const int stride_w,
                       const int dilation_h, const int dilation_w,
                       const int parallel_imgs, const int deformable_group,
                       at::Tensor grad_im);

void deformable_col2im_coord(
    const at::Tensor data_col, const at::Tensor data_im,
    const at::Tensor data_offset, const int channels, const int height,
    const int width, const int ksize_h, const int ksize_w, const int pad_h,
    const int pad_w, const int stride_h, const int stride_w,
    const int dilation_h, const int dilation_w, const int parallel_imgs,
    const int deformable_group, at::Tensor grad_offset);

void modulated_deformable_im2col_cuda(
    const at::Tensor data_im, const at::Tensor data_offset,
    const at::Tensor data_mask, const int batch_size, const int channels,
    const int height_im, const int width_im, const int height_col,
    const int width_col, const int kernel_h, const int kenerl_w,
    const int pad_h, const int pad_w, const int stride_h, const int stride_w,
    const int dilation_h, const int dilation_w, const int deformable_group,
    at::Tensor data_col);

void modulated_deformable_col2im_cuda(
    const at::Tensor data_col, const at::Tensor data_offset,
    const at::Tensor data_mask, const int batch_size, const int channels,
    const int height_im, const int width_im, const int height_col,
    const int width_col, const int kernel_h, const int kenerl_w,
    const int pad_h, const int pad_w, const int stride_h, const int stride_w,
    const int dilation_h, const int dilation_w, const int deformable_group,
    at::Tensor grad_im);

void modulated_deformable_col2im_coord_cuda(
    const at::Tensor data_col, const at::Tensor data_im,
    const at::Tensor data_offset, const at::Tensor data_mask,
    const int batch_size, const int channels, const int height_im,
    const int width_im, const int height_col, const int width_col,
    const int kernel_h, const int kenerl_w, const int pad_h, const int pad_w,
    const int stride_h, const int stride_w, const int dilation_h,
    const int dilation_w, const int deformable_group, at::Tensor grad_offset,
    at::Tensor grad_mask);