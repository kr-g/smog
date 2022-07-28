
# all `smog` cmd-line options


## smog

run `smog -h` for:

    usage: python3 -m smog [options]
    
    simple media organizer
    
    positional arguments:
      {config,scan,find,col,colman,tag,check,xmp,hash}
                            sub-command --help
        config              config --help
        scan                scan --help
        find                find --help
        col                 col --help
        colman              colman --help
        tag                 tag --help
        check               check --help
        xmp                 xmp --help
        hash                hash --help
    
    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         show program's version number and exit
      --verbose, -V         show more info (default: False)
      -debug, -d            display debug info (default: False)
      -timer                display total processing time (default: False)
      -src SRC_DIR, -scan SRC_DIR
                            folder to scan (default: /home/benutzer/Bilder)
      -dest REPO_DIR, -repo REPO_DIR
                            repo folder (default: /home/benutzer/media-repo)
      -repo-db REPO_DB_DIR, -db REPO_DB_DIR
                            repo database folder (default: /home/benutzer/media-
                            db)
      -proc PROC_DIR        processed file folder. subfolder of SRC_DIR. (default:
                            /home/benutzer/Bilder/proc-media)
      -exclude-folder EXCLUDE_DIR [EXCLUDE_DIR ...], -no-scan EXCLUDE_DIR [EXCLUDE_DIR ...]
                            exclude folder from scan
    
    for more information refer to https://github.com/kr-g/smog


## smog config

run `smog config -h` for:

    usage: python3 -m smog [options] config [-h]
                                            [-db-check | -db-init | -db-migrate]
    
    optional arguments:
      -h, --help            show this help message and exit
      -db-check             check database revision
      -db-init              create a new database
      -db-migrate, -db-mig  migrate the database to the lastest version


## smog scan

run `smog scan -h` for:

    usage: python3 -m smog [options] scan [-h] [-tag HASHTAG] [-cleartags]
                                          [-collection COLLECTION]
                                          [FILE [FILE ...]]
    
    positional arguments:
      FILE                  file or folder to scan
    
    optional arguments:
      -h, --help            show this help message and exit
      -tag HASHTAG          hashtag to add to the media. don't add a leading '#'
                            to the tag here.
      -cleartags            clear all hashtags from media before further
                            processing
      -collection COLLECTION, -col COLLECTION
                            add media to collection


## smog find

run `smog find -h` for:

    usage: python3 -m smog [options] find [-h] [-showhash] [-short] [-show-paths]
                                          [-remove] [-id ID] [-before BEFORE]
                                          [-limit LIMIT] [-skip SKIP]
                                          [-tag HASHTAG] [-collection COLLECTION]
                                          [-collection-id COLLECTION-ID]
    
    optional arguments:
      -h, --help           show this help message and exit
      -showhash            show hash
      -short               show short info (only id)
      -show-paths, -paths  show also paths info
      -remove, -rm         remove media completely from database index, all
                           collections and media-repo folder
      -id ID               find media id


## smog col

run `smog col -h` for:

    usage: python3 -m smog [options] col [-h] [-name COLLECTION] [-before BEFORE]
                                         [-limit LIMIT] [-skip SKIP]
    
    optional arguments:
      -h, --help        show this help message and exit
      -name COLLECTION  collection name
      -before BEFORE    find collection before timestamp
      -limit LIMIT      limit result set (default: 50)
      -skip SKIP        skip result result set (default: 0)


## smog colman

run `smog colman -h` for:

    usage: python3 -m smog [options] colman [-h] [-collection-id COL_ID]
                                            [-collection COL_NAME]
                                            [-remove COL_ID [COL_ID ...] | -touch
                                            COL_ID [COL_ID ...] | -rename COL_NAME
                                            | -add-media MEDIA_ID [MEDIA_ID ...] |
                                            -remove-media MEDIA_ID [MEDIA_ID ...]]
    
    optional arguments:
      -h, --help            show this help message and exit
      -collection-id COL_ID, -colid COL_ID
                            collection to use for -add-media, and -rm-media,
                            defaults to latest collection
      -collection COL_NAME, -col COL_NAME
                            collection to use for -add-media, and -rm-media,
                            creates a new collection if not existing
      -remove COL_ID [COL_ID ...], -rm COL_ID [COL_ID ...], -delete COL_ID [COL_ID ...], -del COL_ID [COL_ID ...]
                            remove collection. this does not remove included media
                            from the database index nor from the harddrive
      -touch COL_ID [COL_ID ...]
                            adjusts the collection dates from media
      -rename COL_NAME, -rn COL_NAME
                            rename collection. a literal '%d' in the name will be
                            expanded to the first/ last date(s) of the collection
      -add-media MEDIA_ID [MEDIA_ID ...], -addm MEDIA_ID [MEDIA_ID ...]
                            add media to collection
      -remove-media MEDIA_ID [MEDIA_ID ...], -rm-media MEDIA_ID [MEDIA_ID ...], -rmm MEDIA_ID [MEDIA_ID ...]
                            remove media from collection


## smog tag

run `smog tag -h` for:

    usage: python3 -m smog [options] tag [-h] [-tag HASHTAG]
                                         [-all | -drop | -add-media MEDIA_ID [MEDIA_ID ...]
                                         | -rm-media MEDIA_ID [MEDIA_ID ...]]
    
    optional arguments:
      -h, --help            show this help message and exit
      -tag HASHTAG          hashtag for '-rm', '-add-media', and '-rm-media'
      -all, -list           list all hashtags
      -drop, -rm            remove hashtag from database-index
      -add-media MEDIA_ID [MEDIA_ID ...], -addm MEDIA_ID [MEDIA_ID ...]
                            add hashtag to media
      -rm-media MEDIA_ID [MEDIA_ID ...], -rmm MEDIA_ID [MEDIA_ID ...]
                            remove hashtag from media


## smog check

run `smog check -h` for:

    usage: python3 -m smog [options] check [-h] [-repo | -db | -db-path]
    
    optional arguments:
      -h, --help  show this help message and exit
      -repo       check repo integrity
      -db         check db integrity
      -db-path    check db-index path against file system source path


## smog xmp

run `smog xmp -h` for:

    usage: python3 -m smog [options] xmp [-h] [-types] [-list XMP_FILE]
                                         [-xml | -tags]
    
    optional arguments:
      -h, --help      show this help message and exit
    
    known files:
      -types          list known xmp file extensions
    
    xmp meta:
      -list XMP_FILE  xmp file to inspect
      -xml            list xmp info as xml
      -tags           list xmp info as simple tag list


## smog hash

run `smog hash -h` for:

    usage: python3 -m smog [options] hash [-h] FILE [FILE ...]
    
    positional arguments:
      FILE        calculate file hash
    
    optional arguments:
      -h, --help  show this help message and exit

