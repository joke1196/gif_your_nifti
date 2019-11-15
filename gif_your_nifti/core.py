"""Core functions."""

import os
import nibabel as nb
import numpy as np
from matplotlib.cm import get_cmap
from imageio import mimwrite
from skimage.transform import resize


def parse_filename(filepath):
    """Parse input file path into directory, basename and extension.

    Parameters
    ----------
    filepath: string
        Input name that will be parsed into directory, basename and extension.

    Returns
    -------
    dirname: str
        File directory.
    basename: str
        File name without directory and extension.
    ext: str
        File extension.

    """
    path = os.path.normpath(filepath)
    dirname = os.path.dirname(path)
    filename = path.split(os.sep)[-1]
    basename, ext = filename.split(os.extsep, 1)
    return dirname, basename, ext

def define_output_file_name(filename, outputfile, suffix):
    # Figure out extension
    ext = '.{}'.format(parse_filename(filename)[2])
    outputfilename = filename.replace(ext, '{}.gif'.format(suffix))
    if outputfile:
        outputfilename = '{}.gif'.format(outputfile)
    return outputfilename



def load_and_prepare_image(filename, pixel_num):
    """Load and prepare image data.

    Parameters
    ----------
    filename1: str
        Input file (eg. /john/home/image.nii.gz)
    size: float
        Image resizing factor.

    Returns
    -------
    out_img: numpy array

    """
    # Load NIfTI file
    proxy_img = nb.load(filename)

    if len(proxy_img.shape) == 4:
        #taking the volume in the middle
        vol = proxy_img.shape[-1] / 2
        img_data = proxy_img.dataobj[..., vol]
    else:
        img_data = np.asarray(proxy_img.dataobj)

    # Pad data array with zeros to make the shape isometric
    maximum = np.max(img_data.shape)

    out_img = np.zeros([maximum] * 3)

    a, b, c = img_data.shape
    x, y, z = (list(img_data.shape) - maximum) / -2

    out_img[int(x):a + int(x),
            int(y):b + int(y),
            int(z):c + int(z)] = img_data

    out_img /= out_img.max()  # scale image values between 0-1

    # Resize image by the following factor
    if pixel_num is not None:
        out_img = resize(out_img, [pixel_num] * 3)

    # maximum = int(maximum * size)

    return out_img, pixel_num


def create_mosaic_normal(out_img, maximum):
    """Create grayscale image.

    Parameters
    ----------
    out_img: numpy array
    maximum: int

    Returns
    -------
    new_img: numpy array

    """
    new_img = np.array(
        [np.hstack((
            np.hstack((
                np.flip(out_img[i, :, :], 1).T,
                np.flip(out_img[:, maximum - i - 1, :], 1).T)),
            np.flip(out_img[:, :, maximum - i - 1], 1).T))
         for i in range(maximum)])

    return new_img


def create_mosaic_depth(out_img, maximum):
    """Create an image with concurrent slices represented with colors.

    The image shows you in color what the value of the next slice will be. If
    the color is slightly red or blue it means that the value on the next slide
    is brighter or darker, respectifely. It therefore encodes a certain kind of
    depth into the gif.

    Parameters
    ----------
    out_img: numpy array
    maximum: int

    Returns
    -------
    new_img: numpy array

    """
    # Load normal mosaic image
    new_img = create_mosaic_normal(out_img, maximum)

    # Create RGB image (where red and blue mean a positive or negative shift in
    # the direction of the depicted axis)
    rgb_img = [new_img[i:i + 3, ...] for i in range(maximum - 3)]

    # Make sure to have correct data shape
    out_img = np.rollaxis(np.array(rgb_img), 1, 4)

    # Add the 3 lost images at the end
    out_img = np.vstack(
        (out_img, np.zeros([3] + [o for o in out_img[-1].shape])))

    return out_img


def create_mosaic_RGB(out_img1, out_img2, out_img3, maximum):
    """Create RGB image.

    Parameters
    ----------
    out_img: numpy array
    maximum: int

    Returns
    -------
    new_img: numpy array

    """
    # Load normal mosaic image
    new_img1 = create_mosaic_normal(out_img1, maximum)
    new_img2 = create_mosaic_normal(out_img2, maximum)
    new_img3 = create_mosaic_normal(out_img3, maximum)

    # Create RGB image (where red and blue mean a positive or negative shift
    # in the direction of the depicted axis)
    rgb_img = [[new_img1[i, ...], new_img2[i, ...], new_img3[i, ...]]
               for i in range(maximum)]

    # Make sure to have correct data shape
    out_img = np.rollaxis(np.array(rgb_img), 1, 4)

    # Add the 3 lost images at the end
    out_img = np.vstack(
        (out_img, np.zeros([3] + [o for o in out_img[-1].shape])))

    return out_img


def write_gif_normal(filename, outputfile, pixel_num, fps=18):
    """Procedure for writing grayscale image.

    Parameters
    ----------
    filename: str
        Input file (eg. /john/home/image.nii.gz)
    size: float
        Between 0 and 1.
    fps: int
        Frames per second

    """
    # Load NIfTI and put it in right shape
    out_img, maximum = load_and_prepare_image(filename, pixel_num)

    # Create output mosaic
    new_img = create_mosaic_normal(out_img, maximum)


    # Write gif file
    mimwrite(define_output_file_name(filename, outputfile, ""), new_img,
             format='gif', fps=int(fps))


def write_gif_depth(filename, outputfile, pixel_num, fps=18):
    """Procedure for writing depth image.

    The image shows you in color what the value of the next slice will be. If
    the color is slightly red or blue it means that the value on the next slide
    is brighter or darker, respectifely. It therefore encodes a certain kind of
    depth into the gif.

    Parameters
    ----------
    filename: str
        Input file (eg. /john/home/image.nii.gz)
    size: float
        Between 0 and 1.
    fps: int
        Frames per second

    """
    # Load NIfTI and put it in right shape
    out_img, maximum = load_and_prepare_image(filename, pixel_num)

    # Create output mosaic
    new_img = create_mosaic_depth(out_img, maximum)

    # Write gif file
    mimwrite(define_output_file_name(filename, outputfile, "_depth"), new_img,
             format='gif', fps=int(fps * size))


def write_gif_rgb(filename1, filename2, filename3, pixel_num, fps=18):
    """Procedure for writing RGB image.

    Parameters
    ----------
    filename1: str
        Input file for red channel.
    filename2: str
        Input file for green channel.
    filename3: str
        Input file for blue channel.
    pixel_num: int
        size in pixel of the resulting image
    size: float
        Between 0 and 1.
    fps: int
        Frames per second

    """
    # Load NIfTI and put it in right shape
    out_img1, maximum1 = load_and_prepare_image(filename1, pixel_num)
    out_img2, maximum2 = load_and_prepare_image(filename2, pixel_num)
    out_img3, maximum3 = load_and_prepare_image(filename3, pixel_num)

    if maximum1 == maximum2 and maximum1 == maximum3:
        maximum = maximum1

    # Create output mosaic
    new_img = create_mosaic_RGB(out_img1, out_img2, out_img3, maximum)

    # Generate output path
    out_filename = '{}_{}_{}_rgb.gif'.format(parse_filename(filename1)[1],
                                             parse_filename(filename2)[1],
                                             parse_filename(filename3)[1])
    out_path = os.path.join(parse_filename(filename1)[0], out_filename)

    # Write gif file
    mimwrite(out_path, new_img, format='gif', fps=int(fps))


def write_gif_pseudocolor(filename, outputfile, pixel_num, fps=18, colormap='hot'):
    """Procedure for writing pseudo color image.

    The colormap can be any colormap from matplotlib.

    Parameters
    ----------
    filename1: str
        Input file (eg. /john/home/image.nii.gz)
    size: float
        Between 0 and 1.
    pixel_num: int
        size in pixel of the resulting image
    fps: int
        Frames per second
    colormap: str
        Name of the colormap that will be used.

    """
    # Load NIfTI and put it in right shape
    out_img, maximum = load_and_prepare_image(filename, pixel_num)

    # Create output mosaic
    new_img = create_mosaic_normal(out_img, maximum)

    # Transform values according to the color map
    cmap = get_cmap(colormap)
    color_transformed = [cmap(new_img[i, ...]) for i in range(maximum)]
    cmap_img = np.delete(color_transformed, 3, 3)

    # Write gif file
    mimwrite(define_output_file_name(filename, outputfile, "_{}".format(colormap)),
             cmap_img, format='gif', fps=int(fps))
