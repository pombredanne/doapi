import argparse
from   six.moves import map
from   .         import _util as util
from   ..image   import Image

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-image')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    showopts = cmd_show.add_mutually_exclusive_group()
    showopts.add_argument('--distribution', action='store_true')
    showopts.add_argument('--application', action='store_true')
    showopts.add_argument('--type')
    showopts.add_argument('--private', action='store_true')
    cmd_show.add_argument('-M', '--multiple', action='store_true')
    cmd_show.add_argument('image', nargs='*')

    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('-M', '--multiple', action='store_true')
    cmd_delete.add_argument('image', nargs='+')

    cmd_update = cmds.add_parser('update')
    cmd_update.add_argument('--unique', action='store_true')
    cmd_update.add_argument('image')
    cmd_update.add_argument('name')

    cmd_transfer = cmds.add_parser('transfer', parents=[util.waitopts])
    cmd_transfer.add_argument('-M', '--multiple', action='store_true')
    cmd_transfer.add_argument('region')
    cmd_transfer.add_argument('image', nargs='+')

    cmd_convert = cmds.add_parser('convert', parents=[util.waitopts])
    cmd_convert.add_argument('-M', '--multiple', action='store_true')
    cmd_convert.add_argument('image', nargs='+')

    util.add_actioncmds(cmds, 'image')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)

    if args.cmd == 'show':
        if args.distribution:
            if args.image:
                util.die('--distribution and image arguments are mutually exclusive')
            util.dump(client.fetch_all_distribution_images())
        elif args.application:
            if args.image:
                util.die('--application and image arguments are mutually exclusive')
            util.dump(client.fetch_all_application_images())
        elif args.type:
            if args.image:
                util.die('--type and image arguments are mutually exclusive')
            util.dump(client.fetch_all_images(type=args.type))
        elif args.private:
            if args.image:
                util.die('--private and image arguments are mutually exclusive')
            util.dump(client.fetch_all_private_images())
        elif args.image:
            util.dump(cache.get_images(args.image, multiple=args.multiple,
                                                   hasM=True))
        else:
            util.dump(client.fetch_all_images())

    elif args.cmd == 'delete':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        for i in imgs:
            i.delete()

    elif args.cmd == 'update':
        cache.check_name_dup("image", args.name, args.unique)
        img = cache.get_image(args.image, multiple=False)
        util.dump(img.update_image(args.name))

    elif args.cmd == 'transfer':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        acts = (i.transfer(args.region) for i in imgs)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'convert':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        acts = map(Image.convert, imgs)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd in ('act', 'actions', 'wait'):
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        util.do_actioncmd(args, client, imgs)

    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))


if __name__ == '__main__':
    main()
