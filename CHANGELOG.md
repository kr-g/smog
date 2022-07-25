
see [`BACKLOG`](https://github.com/kr-g/smog/blob/main/BACKLOG.md)
for open development tasks and limitations.


# CHANGELOG


# next version v0.0.4 - ???

- 


# version v0.0.3 - 20220725

- new for `colman`
  - `-add-media`, adding media to a collection
  - `-rm-mdeia`, removing media from a collection
  - `touch`, sets the first/last timestamps fresh 
    - resolves BUG in `scan` with `-col`
- sub-cmd `tag` for hashtag and media handling
- database schema revision check during startup
- `find` filter on collection id
- license change
- 


## version v0.0.2 - 20220712

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