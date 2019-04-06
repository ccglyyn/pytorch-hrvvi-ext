import random


class Transform:

    def __init__(self):
        pass

    def __call__(self, input, target):
        pass


class JointTransform(Transform):

    def __init__(self, transform=None):
        super().__init__()
        self.transform = transform

    def __call__(self, input, target):
        return self.transform(input, target)


class InputTransform(Transform):

    def __init__(self, transform):
        super().__init__()
        self.transform = transform

    def __call__(self, input, target):
        return self.transform(input), target


class TargetTransform(Transform):

    def __init__(self, transform):
        super().__init__()
        self.transform = transform

    def __call__(self, input, target):
        return input, self.transform(target)


class Compose(Transform):
    """Composes several transforms together.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.

    Example:
        >>> transforms.Compose([
        >>>     transforms.CenterCrop(10),
        >>>     transforms.ToTensor(),
        >>> ])
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img, target):
        for t in self.transforms:
            img, target = t(img, target)
        return img, target

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string


class UseOrigin(Transform):
    """Use the original image and annotations.
    """

    def __init__(self):
        pass

    def __call__(self, img, target):
        return img, target

    def __repr__(self):
        format_string = self.__class__.__name__ + '()'
        return format_string


class RandomChoice(Transform):
    """Apply single transformation randomly picked from a list.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.

    Example:
        >>> transforms.RandomChoice([
        >>>     transforms.CenterCrop(10),
        >>>     transforms.ToTensor(),
        >>> ])
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img, target):
        t = random.choice(self.transforms)
        img, target = t(img, target)
        return img, target

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n'
            format_string += '    {0}'.format(t)
        format_string += '\n)'
        return format_string