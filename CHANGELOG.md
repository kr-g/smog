
see [`BACKLOG`](https://github.com/kr-g/smog/blob/main/BACKLOG.md)
for open development tasks and limitations.


# Changelog

## version v0.0.2 - ???

- support of xmp metadata added
  - support of various file types containing xmp metadata
    - `xmp -types` will list all file extensions
  - cmd-line `xmp` sub-command for query xmp metadata
- [`sqlalchemy`](https://www.sqlalchemy.org/) orm integration for media database
- introduced pipe style processing of media items
- enhanced cmd-line with `scan` sub-command
- cmd-line `find` sub-command 
- cmd-line `scan` hashtag 
- cmd-line `scan` collection 
- added `alembic` database migration
- added `config` sub-command with `-db-init` and `-db-migrate`
- `find` filter on hashtag(s)
- `find` filter on collection name
- `find` short display option showing column `media.id`
- `find` with `-remove` for deleting from db-index and repo (file-system)
- `col` for inspecting collections
- `colman` with `remove` for deleting a collection from the db-index
- 


## version v0.0.1 - 20220626

- first release
- 