import sys
import time
import json
import argparse

from .const import (
    VERSION,
    DEFAULT_MEDIA_REPO,
    DEFAULT_MEDIA_DB,
    DEFAULT_REL_PROC,
    SMOG_DB_NAME,
)

from .file import FileStat

from .dbconf import DBConf, SqliteConf
from .dbmedia import MediaDB
from .dbschema import MediaCollection, MediaCollectionItem, MediaHashtag

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import get_tags, xmp_dict, cleanup_xmp_dict, xmp_tags

from dateutil.parser import isoparse
from datetime import datetime as DateTime

from .context import (
    Context,
    CtxPipe,
    CtxTerm,
    CtxStop,
    CtxPrint,
    CtxProcessor,
)

from .ctxflow import build_scan_flow

#

args = None
debug = False
verbose = False


def dprint(*args, **kwargs):
    global debug
    debug and print("DEBUG", *args, **kwargs)


def vprint(*args, **kwargs):
    global verbose
    verbose and print(*args, **kwargs)


def wprint(*args, **kwargs):
    print("WARNING", *args, **kwargs)


def eprint(*args, **kwargs):
    print("ERROR", *args, **kwargs, file=sys.stderr)


def print_err(*args, **kwargs):
    eprint(*args, **kwargs)


#


def get_default_pic_folder():
    flds = ["~/Bilder", "~/Pictures"]
    for d in flds:
        f = FileStat(d, prefetch=True)
        if f.is_dir():
            return f.name
    return FileStat().name


def is_folder_or_die(f):
    if f.exists() and not f.is_dir():
        eprint("not a folder", f.name)
        sys.exit(1)


#


def check_db_revision(args):

    CHKC = getarg("db_check_call_print", True)

    CHKC and print("checking db revision")

    from alembic.config import Config as AlembicConfig
    from alembic.runtime import migration
    from alembic import script
    import smog_alembic

    inid = FileStat(smog_alembic.__file__).dirname()
    ini = FileStat(inid).join(["alembic.ini"])

    alembic_cfg = AlembicConfig(ini.name)
    if not CHKC:
        alembic_cfg = AlembicConfig()

    # overwrite location
    alembic_cfg.set_main_option("script_location", inid)

    db_conf = args.db_conf
    engine = db_conf.open_db()

    directory = script.ScriptDirectory.from_config(alembic_cfg)

    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        context = migration.MigrationContext.configure(connection)
        current = set(context.get_current_heads())
        latest = set(directory.get_heads())

        CHKC and print("current", current)
        CHKC and print("latest", latest)

    return current == latest


def config_func(args):

    if args.db_check:
        return check_db_revision(args)

    if args.db_init or args.db_migrate:

        needtocreate = args.needtocreate
        db_path = args.db_path
        db_conf = args.db_conf

        from alembic.config import Config as AlembicConfig
        from alembic import command
        import smog_alembic

        inid = FileStat(smog_alembic.__file__).dirname()
        ini = FileStat(inid).join(["alembic.ini"])

        alembic_cfg = AlembicConfig(ini.name)
        # overwrite location
        alembic_cfg.set_main_option("script_location", inid)

        engine = db_conf.open_db()

        with engine.begin() as connection:
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, "head")

        return

    print("what? use --help")


#


def scan_func(args):

    pipe = CtxPipe(args.ctx)

    build_scan_flow(pipe)

    pipe.reset()

    while True:
        try:
            pipe.process()
        except StopIteration:
            break

    args.ctx.print(
        "total files scanned",
        args.ctx.NO_FILES,
        "\n",
        "files copied",
        args.ctx.NO_COPY_FILES,
        "\n",
        "file copy failed",
        args.ctx.NO_COPY_FILES_FAILED,
        "\n",
        "files moved",
        args.ctx.NO_MOVE_FILES,
        "\n",
        "file move failed",
        args.ctx.NO_MOVE_FILES_FAILED,
        "\n",
        "files renamed",
        args.ctx.NO_COPY_FILES_RENAMED,
        "\n",
        "db rec created",
        args.ctx.NO_DB_CREATED,
        "\n",
        "db rec updated (incl created)",
        args.ctx.NO_DB_UPDATED,
    )


#


def hash_func(args):
    for fnam in args.hash_file:
        f = FileStat(fnam).read_stat()
        if not f.exists():
            print("file not found", f)
            continue
        if f.is_dir():
            print("file required, folder found", f)
            continue
        print(f.name, "->", f.hash())


#


def print_rec(args, rec):
    pargs = [rec.id]
    if not args.find_short:
        pargs.extend([rec.timestamp, rec.repopath])
    if args.find_show_hash:
        pargs.append(rec.hash)
    print(*pargs)

    if args.find_show_paths:
        for p in rec.paths:
            print("->", p.path)


def find_func(args):
    if args.find_id:
        rec = args.ctx.db.qry_media_id(args.find_id)
        if rec:
            print_rec(args, rec)
            return
        eprint("not found", args.find_id)
        sys.exit(1)

    _limit = args.find_limit
    if _limit <= 0:
        eprint("limit must be a positive number > 0")
        sys.exit(1)

    _skip = args.find_skip
    if _skip < 0:
        eprint("skip must be a positive number >= 0")
        sys.exit(1)
    if _skip == 0:
        _skip = None

    qry = args.ctx.db.qry_media_stream(
        args.find_before,
        skip_offset=_skip,
        hashtag=args.find_hashtag,
        collection=args.find_collection,
        collectionid=args.find_collection_id,
    )

    for rec in qry:
        _limit -= 1
        if _limit < 0:
            print(f"showing {args.find_limit} records...")
            break
        print_rec(args, rec)
        if args.find_remove:
            print("drop db index for", rec.id)
            args.ctx.db.remove(rec)
            f = FileStat(args.ctx.repodir).join([rec.repopath])
            print("remove path", f.name)
            f.remove()

    if args.find_remove:
        print("commit database index")
        args.ctx.db.commit()


#


def collection_func(args):

    _limit = args.col_limit
    if _limit <= 0:
        eprint("limit must be a positive number > 0")
        sys.exit(1)

    _skip = args.col_skip
    if _skip < 0:
        eprint("skip must be a positive number >= 0")
        sys.exit(1)
    if _skip == 0:
        _skip = None

    col_name = args.col_name

    qry = args.ctx.db.qry_media_collection_name_stream(
        name=args.col_name, timestamp=args.col_before, skip_offset=_skip
    )

    for rec in qry:
        _limit -= 1
        if _limit < 0:
            print(f"showing {args.col_limit} records...")
            break
        print(rec.id, rec.name, rec.first_media, rec.last_media)


#


def filter_mediaitem_id(mediaitems, id):
    for mi in mediaitems:
        if mi.media_col_item == id:
            return mi


def colman_func(args):

    if args.colman_touch:
        for colid in args.colman_touch:
            col = args.ctx.db.qry_media_collection(colid)
            if col is None:
                wprint("not found", colid)
                continue

            for mediaitem in col.mediaitems:
                col.first_media = min(col.first_media, mediaitem.media.timestamp)
                col.last_media = max(col.last_media, mediaitem.media.timestamp)

            args.ctx.db.upsert(col, auto_commit=True)

        return

    if args.colman_remove:
        for colid in args.colman_remove:
            rec = args.ctx.db.qry_media_collection(colid)
            if rec is None:
                wprint("not found", colid)
                continue
            print("remove from database", rec.id, rec.name)
            args.ctx.db.remove(rec, auto_commit=True)

        return

    col = None

    if args.colman_add or args.colman_remove:

        if args.colman_name:
            col = args.ctx.db.qry_media_collection_name(args.colman_name)
            if col is None:
                col = DBConf.create_new_with_id(MediaCollection)
                col.name = args.colman_name
                col.first_media = DateTime.utcnow()
                col.last_media = DateTime.fromtimestamp(0)

        if col is None:
            if args.colman_id is None:
                col = args.ctx.db.qry_media_collection_name()
                print("using default collection", col.id, col.name)
            else:
                col = args.ctx.db.qry_media_collection(args.colman_id)
                if col is None:
                    eprint("collection not found")
                    return 1

        mediaitems = col.mediaitems

        if args.colman_add:
            for mediaid in args.colman_add:

                media = args.ctx.db.qry_media_id(mediaid)
                if media is None:
                    eprint("media not found", mediaid)
                    continue

                mi = filter_mediaitem_id(mediaitems, mediaid)
                if mi:
                    vprint("media already exists in collection", mediaid)
                    continue

                mediaitem = DBConf.create_new_with_id(MediaCollectionItem)
                mediaitem.media_collection = col
                mediaitem.media = media

                vprint("add media to collection", mediaid)
                args.ctx.db.upsert(mediaitem)
                col.mediaitems.append(mediaitem)

        if args.colman_remove:
            for mediaid in args.colman_remove:

                media = args.ctx.db.qry_media_id(mediaid)
                if media is None:
                    eprint("media not found", mediaid)
                    continue

                mediaitem = filter_mediaitem_id(mediaitems, mediaid)
                if mediaitem is None:
                    vprint("media not in collection", mediaid)
                    continue

                vprint("remove media from collection", mediaid)
                args.ctx.db.remove(mediaitem)
                mediaitems.remove(mediaitem)

        for mediaitem in mediaitems:
            col.first_media = min(col.first_media, mediaitem.media.timestamp)
            col.last_media = max(col.last_media, mediaitem.media.timestamp)

        args.ctx.db.upsert(col)
        args.ctx.db.commit()

        return

    print("what? use --help")


#


def filter_hashtag(hashtags, tag):
    for rec in hashtags:
        if rec.hashtag == tag:
            return rec


def hashtag_func(args):
    if args.hashtag_all:
        for hashtag in args.ctx.db.qry_hashtag():
            print(hashtag)
        return

    hashtag = args.hashtag_tag

    if hashtag:
        hashtag = hashtag.strip().lower()
        if len(hashtag) == 0:
            hashtag = None

    if hashtag is None:
        eprint("hashtag missing")
        return 1

    if hashtag.find("#") >= 0:
        eprint("hashtag contains '#'", hashtag)
        return 1

    hashtag = "#" + hashtag

    if args.hashtag_rm:
        rc = args.ctx.db.qry_hashtag_drop(hashtag)
        args.ctx.db.commit()
        return rc

    if args.hashtag_media_add:
        for mediaid in args.hashtag_media_add:
            media = args.ctx.db.qry_media_id(mediaid)
            if media is None:
                wprint("media not found", mediaid)
                continue
            hashtags = media.hashtags
            rec = filter_hashtag(hashtags, hashtag)
            if rec:
                vprint("media already tagged", mediaid)
                continue
            mediahashtag = DBConf.create_new_with_id(MediaHashtag)
            mediahashtag.media = media
            mediahashtag.hashtag = hashtag

            media.hashtags.append(mediahashtag)
            args.ctx.db.upsert(mediahashtag)
            args.ctx.db.upsert(media)
            args.ctx.db.commit()
        return

    if args.hashtag_media_rm:
        for mediaid in args.hashtag_media_rm:
            media = args.ctx.db.qry_media_id(mediaid)
            if media is None:
                wprint("media not found", mediaid)
                continue
            hashtags = media.hashtags
            rec = filter_hashtag(hashtags, hashtag)
            if rec is None:
                vprint("media not tagged", mediaid)
                continue

            media.hashtags.remove(rec)
            args.ctx.db.remove(rec)
            args.ctx.db.upsert(media)
            args.ctx.db.commit()
        return

    print("what? use --help")


#


def xmp_func(args):
    if args.xmp_filetypes:
        dump_guessed()
        return
    if args.xmp_file:

        f = FileStat(args.xmp_file)
        if not f.exists():
            print_err("file not found", f.name)
            return 1
        if not f.is_file():
            print_err("not a file", f.name)
            return 1

        if args.xmp_xml:
            meta = xmp_meta(args.xmp_file)
            meta = str(meta)
            print(meta)
            return

        xmp = xmp_dict(args.xmp_file)
        xmp_c = cleanup_xmp_dict(xmp)

        if args.xmp_tag:
            tags = xmp_tags(xmp_c)
            for k, v in tags:
                print(k, v)
            return

        print(json.dumps(xmp_c, indent=4))


def getarg(nam, defval=None):
    global args
    return args.__dict__.get(nam, defval)


def main_func(mkcopy=True):

    global debug, verbose

    parser = argparse.ArgumentParser(
        prog="smog",
        usage="python3 -m %(prog)s [options]",
        description="simple media organizer",
        epilog="for more information refer to https://github.com/kr-g/smog",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "--verbose",
        "-V",
        dest="verbose",
        action="store_true",
        help="show more info (default: %(default)s)",
        default=verbose,
    )
    parser.add_argument(
        "-debug",
        "-d",
        dest="debug",
        action="store_true",
        help="display debug info (default: %(default)s)",
        default=debug,
    )

    parser.add_argument(
        "-timer",
        dest="show_time",
        action="store_true",
        help="display total processing time (default: %(default)s)",
        default=False,
    )

    base = get_default_pic_folder()

    parser.add_argument(
        "-src",
        "-scan",
        type=str,
        dest="base",
        action="store",
        metavar="SRC_DIR",
        help="folder to scan (default: %(default)s)",
        default=base,
    )

    dest_repo = FileStat(DEFAULT_MEDIA_REPO)

    parser.add_argument(
        "-dest",
        "-repo",
        type=str,
        dest="dest_repo",
        action="store",
        metavar="REPO_DIR",
        help="repo folder (default: %(default)s)",
        default=dest_repo.name,
    )

    db_path = FileStat(DEFAULT_MEDIA_DB)

    parser.add_argument(
        "-repo-db",
        "-db",
        type=str,
        dest="repo_db_path",
        action="store",
        metavar="REPO_DB_DIR",
        help="repo database folder (default: %(default)s)",
        default=db_path.name,
    )

    proc_dir = FileStat(base).join([DEFAULT_REL_PROC])

    parser.add_argument(
        "-proc",
        type=str,
        dest="proc_dir",
        action="store",
        metavar="PROC_DIR",
        help="processed file folder. subfolder of SRC_DIR. (default: %(default)s)",
        default=proc_dir.name,
    )

    parser.add_argument(
        "-exclude-folder",
        "-no-scan",
        type=str,
        dest="exclude_dirs",
        action="store",
        nargs="+",
        metavar="EXCLUDE_DIR",
        help="exclude folder from scan",
        default=None,
    )

    subparsers = parser.add_subparsers(help="sub-command --help")

    # init

    config_parser = subparsers.add_parser("config", help="config --help")
    config_parser.set_defaults(func=config_func)

    config_xgroup = config_parser.add_mutually_exclusive_group()

    config_xgroup.add_argument(
        "-db-check",
        dest="db_check",
        action="store_true",
        help="check database revision",
        default=False,
    )

    config_xgroup.add_argument(
        "-db-init",
        dest="db_init",
        action="store_true",
        help="create a new database",
        default=False,
    )

    config_xgroup.add_argument(
        "-db-migrate",
        "-db-mig",
        dest="db_migrate",
        action="store_true",
        help="migrate the database to the lastest version",
        default=False,
    )

    # scan

    scan_parser = subparsers.add_parser("scan", help="scan --help")
    scan_parser.set_defaults(func=scan_func)
    scan_parser.add_argument(
        "-tag",
        dest="scan_hashtag",
        metavar="HASHTAG",
        type=str,
        action="append",
        help="hashtag to add to the media. don't add a leading '#' to the tag here.",
        default=None,
    )
    scan_parser.add_argument(
        "-cleartags",
        dest="scan_cleartags",
        action="store_true",
        help="clear all hashtags from media before further processing",
        default=False,
    )
    scan_parser.add_argument(
        "-collection",
        "-col",
        dest="scan_collection",
        metavar="COLLECTION",
        type=str,
        help="add media to collection",
        default=None,
    )

    scan_parser.add_argument(
        "scanlist",
        metavar="FILE",
        default=None,
        nargs="*",
        help="file or folder to scan",
    )

    # hash

    hash_parser = subparsers.add_parser("hash", help="hash --help")
    hash_parser.set_defaults(func=hash_func)
    hash_parser.add_argument(
        "hash_file", metavar="FILE", type=str, nargs="+", help="calculate file hash"
    )

    # find

    find_parser = subparsers.add_parser("find", help="find --help")
    find_parser.set_defaults(func=find_func)

    find_parser.add_argument(
        "-showhash",
        dest="find_show_hash",
        action="store_true",
        help="show hash",
        default=False,
    )
    find_parser.add_argument(
        "-short",
        dest="find_short",
        action="store_true",
        help="show short info (only id)",
        default=False,
    )
    find_parser.add_argument(
        "-show-paths",
        "-paths",
        dest="find_show_paths",
        action="store_true",
        help="show also paths info",
        default=False,
    )

    find_parser.add_argument(
        "-remove",
        "-rm",
        dest="find_remove",
        action="store_true",
        help="remove media completely from database index, all collections and media-repo folder",
        default=False,
    )

    find_xgroup = find_parser.add_mutually_exclusive_group()

    # find_id_group = find_xgroup.add_argument_group("id", "id options")
    find_xgroup.add_argument(
        "-id",
        dest="find_id",
        metavar="ID",
        type=str,
        help="find media id",
        default=None,
    )
    find_before_group = find_xgroup.add_argument_group("before", "before options")
    find_before_group.add_argument(
        "-before",
        dest="find_before",
        metavar="BEFORE",
        type=isoparse,
        help="find media before timestamp (will accept any iso format with '-' or dots, or not)",
        default=None,
    )
    find_before_group.add_argument(
        "-limit",
        dest="find_limit",
        metavar="LIMIT",
        type=int,
        help="limit result set  (default: %(default)s)",
        default=50,
    )
    find_before_group.add_argument(
        "-skip",
        dest="find_skip",
        metavar="SKIP",
        type=int,
        help="skip result result set  (default: %(default)s)",
        default=0,
    )
    find_before_group.add_argument(
        "-tag",
        dest="find_hashtag",
        metavar="HASHTAG",
        type=str,
        action="append",
        help="hashtag filter. don't add a leading '#' to the tag here",
        default=None,
    )
    find_before_group.add_argument(
        "-collection",
        "-col",
        dest="find_collection",
        metavar="COLLECTION",
        type=str,
        help="collection filter",
        default=None,
    )
    find_before_group.add_argument(
        "-collection-id",
        "-colid",
        dest="find_collection_id",
        metavar="COLLECTION-ID",
        type=str,
        help="collection id filter",
        default=None,
    )

    # collection

    collection_parser = subparsers.add_parser("col", help="col --help")
    collection_parser.set_defaults(func=collection_func)

    collection_parser.add_argument(
        "-name",
        dest="col_name",
        metavar="COLLECTION",
        type=str,
        help="collection name",
        default=None,
    )

    collection_parser.add_argument(
        "-before",
        dest="col_before",
        metavar="BEFORE",
        type=isoparse,
        help="find collection before timestamp",
        default=None,
    )

    collection_parser.add_argument(
        "-limit",
        dest="col_limit",
        metavar="LIMIT",
        type=int,
        help="limit result set  (default: %(default)s)",
        default=50,
    )

    collection_parser.add_argument(
        "-skip",
        dest="col_skip",
        metavar="SKIP",
        type=int,
        help="skip result result set  (default: %(default)s)",
        default=0,
    )

    # collection manager

    colman_parser = subparsers.add_parser("colman", help="colman --help")
    colman_parser.set_defaults(func=colman_func)

    colman_parser.add_argument(
        "-collection-id",
        "-colid",
        dest="colman_id",
        metavar="COL_ID",
        type=str,
        help="collection to use for -add-media, and -rm-media, defaults to latest collection",
        default=None,
    )
    colman_parser.add_argument(
        "-collection",
        "-col",
        dest="colman_name",
        metavar="COL_NAME",
        type=str,
        help="collection to use for -add-media, and -rm-media, creates a new collection if not existing",
        default=None,
    )

    colman_x_group = colman_parser.add_mutually_exclusive_group()

    colman_x_group.add_argument(
        "-remove",
        "-rm",
        "-delete",
        "-del",
        dest="colman_remove",
        metavar="COL_ID",
        nargs="+",
        type=str,
        help="remove collection. this does not remove included media from the database index nor from the harddrive",
        default=None,
    )
    colman_x_group.add_argument(
        "-touch",
        dest="colman_touch",
        metavar="COL_ID",
        nargs="+",
        type=str,
        help="adjusts the collection dates from media",
        default=None,
    )

    colman_x_group.add_argument(
        "-add-media",
        "-addm",
        dest="colman_add",
        metavar="MEDIA_ID",
        nargs="+",
        type=str,
        help="add media to collection",
        default=None,
    )
    colman_x_group.add_argument(
        "-remove-media",
        "-rm-media",
        "-rmm",
        dest="colman_remove",
        metavar="MEDIA_ID",
        nargs="+",
        type=str,
        help="remove media from collection",
        default=None,
    )

    # xmp

    hashtag_parser = subparsers.add_parser("tag", help="tag --help")
    hashtag_parser.set_defaults(func=hashtag_func)

    hashtag_parser.add_argument(
        "-tag",
        dest="hashtag_tag",
        metavar="HASHTAG",
        type=str,
        default=None,
        help="hashtag for '-rm', '-add-media', and '-rm-media'",
    )

    hashtag_x_group = hashtag_parser.add_mutually_exclusive_group()

    hashtag_x_group.add_argument(
        "-all",
        "-list",
        dest="hashtag_all",
        action="store_true",
        default=False,
        help="list all hashtags",
    )
    hashtag_x_group.add_argument(
        "-drop",
        "-rm",
        dest="hashtag_rm",
        action="store_true",
        default=False,
        help="remove hashtag from database-index",
    )

    hashtag_x_group.add_argument(
        "-add-media",
        "-addm",
        dest="hashtag_media_add",
        metavar="MEDIA_ID",
        nargs="+",
        type=str,
        help="add hashtag to media",
    )
    hashtag_x_group.add_argument(
        "-rm-media",
        "-rmm",
        dest="hashtag_media_rm",
        metavar="MEDIA_ID",
        nargs="+",
        type=str,
        help="remove hashtag from media",
    )

    # xmp

    xmp_parser = subparsers.add_parser("xmp", help="xmp --help")
    xmp_parser.set_defaults(func=xmp_func)

    xmptypes = xmp_parser.add_argument_group("known files")
    xmptypes.add_argument(
        "-types",
        dest="xmp_filetypes",
        action="store_true",
        default=False,
        help="list known xmp file extensions",
    )

    xmpmeta = xmp_parser.add_argument_group("xmp meta")
    xmpmeta.add_argument(
        "-list",
        type=str,
        dest="xmp_file",
        action="store",
        help="xmp file to inspect",
        default=None,
    )

    xmp_show_opts = xmpmeta.add_mutually_exclusive_group()
    xmp_show_opts.add_argument(
        "-xml",
        dest="xmp_xml",
        action="store_true",
        help="list xmp info as xml",
        default=False,
    )
    xmp_show_opts.add_argument(
        "-tags",
        dest="xmp_tag",
        action="store_true",
        help="list xmp info as simple tag list",
        default=False,
    )

    #

    global args
    args = parser.parse_args()

    debug = args.debug
    dprint("arguments", args)

    verbose = args.verbose

    args.base = FileStat(args.base)
    is_folder_or_die(args.base)

    args.dest_repo = FileStat(args.dest_repo)
    is_folder_or_die(args.dest_repo)

    if args.base.name == args.dest_repo.name:
        print_err("in place processing not supported")
        sys.exit(1)

    args.proc_dir = FileStat(args.proc_dir)
    is_folder_or_die(args.proc_dir)

    if args.exclude_dirs:
        args.exclude_dirs = list(
            map(lambda x: FileStat(x, prefetech=True), args.exclude_dirs)
        )

        for nam in args.exclude_dirs:
            f = FileStat(nam, prefetch=True)
            is_folder_or_die(f)
        args.exclude_dirs = list(map(lambda x: x.name, args.exclude_dirs))

    # todo
    # refactor for other db than sqlite
    dbdir = FileStat(args.repo_db_path)
    if dbdir.exists():
        if not dbdir.is_dir():
            print_err("db folder parameter is not a folder", dbdir.name)
            sys.exit(1)
    else:
        dprint("create db folder", dbdir.name)
        dbdir.makedirs(is_file=False)

    dbf = dbdir.clone().join([SMOG_DB_NAME])
    needtocreate = not dbf.exists()
    args.needtocreate = needtocreate

    dbconf = SqliteConf(SMOG_DB_NAME, path=dbdir.name)
    args.db_path = dbf
    args.db_conf = dbconf

    if getarg("db_check") or getarg("db_init") or getarg("db_migrate"):
        return config_func(args)
    else:
        vprint("checking db revision")
        args.db_check_call_print = False
        rev_ok = check_db_revision(args)
        if not rev_ok:
            eprint(
                "database not latest revision. backup and upgrade with '-db-migrate'"
            )
            sys.exit(1)

    if needtocreate:
        print_err("database not found. run \n\t")
        print("smog config -db-init")
        sys.exit(1)

    db = MediaDB(dbconf)

    hashtag = getarg("scan_hashtag")
    if hashtag:
        for ht in hashtag:
            if ht.find("#") >= 0:
                print_err("hashtag contains '#'", ht)
                sys.exit(1)

    args.ctx = Context(
        args.base.name,
        args.dest_repo.name,
        args.proc_dir.name,
        db=db,
        hashtag=hashtag,
        cleartags=getarg("scan_cleartags"),
        collection=getarg("scan_collection"),
        excludedirs=args.exclude_dirs,
        scanlist=getarg("scanlist"),
        verbose=verbose,
        debug=debug,
    )

    if "func" in args:
        dprint("call func", args.func.__name__)

        t_start = time.time()
        rc = args.func(args)
        t_stop = time.time()

        rc = rc if rc != None else 0

        if args.show_time:
            t_used = DateTime.fromtimestamp(t_stop) - DateTime.fromtimestamp(t_start)
            t_secs = t_used.total_seconds()
            mins = int(t_secs / 60)
            hrs = int(mins / 60)
            secs = int(t_secs % 60)
            print("total run time", mins, "minutes", secs, "secs")

        return rc

    print("what? use --help")
