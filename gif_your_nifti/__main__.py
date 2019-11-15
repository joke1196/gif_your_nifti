"""Main entry point."""

import argparse
import gif_your_nifti.config as cfg
from gif_your_nifti import core, __version__
import warnings  # mainly for ignoring imageio warnings
warnings.filterwarnings("ignore")


def main():
    """Commandline interface."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'filename',  metavar='path', nargs='+',
        help="Path to image. Multiple paths can be provided."
        )
    parser.add_argument(
        '--mode', type=str, required=False,
        metavar=cfg.mode, default=cfg.mode,
        help="Gif creation mode. Available options are: 'normal', \
        'pseudocolor', 'depth', 'rgb'"
        )
    parser.add_argument(
        '--fps', type=int, required=False,
        metavar=cfg.fps, default=cfg.fps,
        help="Frames per second."
        )
    parser.add_argument(
        '--size', type=float, required=False,
        metavar=cfg.size, default=cfg.size,
        help="Image resizing factor."
        )
    parser.add_argument(
        '--cmap', type=str, required=False,
        metavar=cfg.cmap, default=cfg.cmap,
        help="Color map. Used only in combination with 'pseudocolor' mode."
        )

    parser.add_argument(
        '--output', type=str, required=False,
        metavar=cfg.output, default=cfg.output,
        help="Define a name for the output file"
    )

    parser.add_argument(
        '--pixel', type=int, required=False,
        metavar=cfg.pixel_num, default=cfg.pixel_num,
        help="Define a maximum size for the output image"
    )

    args = parser.parse_args()
    cfg.mode = (args.mode).lower()
    cfg.size = args.size
    cfg.fps = args.fps
    cfg.cmap = args.cmap
    cfg.output = args.output
    cfg.pixel_num = args.pixel_num

    # Welcome message
    welcome_str = '{} {}'.format('gif_your_nifti', __version__)
    welcome_decor = '=' * len(welcome_str)
    print('{}\n{}\n{}'.format(welcome_decor, welcome_str, welcome_decor))

    print('Selections:')
    print('  mode        = {}'.format(cfg.mode))
    print('  fps         = {}'.format(cfg.fps))
    print('  outputfile  = {}'.format(cfg.output))
    print('  pixel_num   = {}'.format(cfg.pixel_num))

    # Determine gif creation mode
    if cfg.mode in ['normal', 'pseudocolor', 'depth']:
        for f in args.filename:
            if cfg.mode == 'normal':
                core.write_gif_normal(f, cfg.output, cfg.pixel_num,cfg.size, cfg.fps)
            elif cfg.mode == 'pseudocolor':
                print('  cmap        = {}'.format(cfg.cmap))
                core.write_gif_pseudocolor(f, cfg.output, cfg.pixel_num, cfg.size, cfg.fps, cfg.cmap)
            elif cfg.mode == 'depth':
                core.write_gif_depth(f, cfg.output, cfg.pixel_num,cfg.size, cfg.fps)

    elif cfg.mode == 'rgb':
        if len(args.filename) != 3:
            raise ValueError('RGB mode requires 3 input files.')
        else:
            core.write_gif_rgb(args.filename[0], args.filename[1],
                               args.filename[2], cfg.pixel_num,cfg.size, cfg.fps)
    else:
        raise ValueError("Unrecognized mode.")

    print('Finished.')


if __name__ == "__main__":
    main()
