[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# smog 

simple media organizer - organize media files 

e.g. a file `20220202_093343.jpg`
is moved into a folder structure like 
`~/media-repo/2022/02/20220202/20220202_093343.jpg`.

if possible xmp/exif metadata is used to determine the date,
otherwise it's extracted from the name (experimental).


## what is a media ?

a media is a file what transports kind of information, such as:

- photo
- video
- pdf 
- ...


# what's new ?

check
[`CHANGELOG`](https://github.com/kr-g/smog/blob/main/CHANGELOG.md)
for latest ongoing, or upcoming news.


# limitations

check 
[`BACKLOG`](https://github.com/kr-g/smog/blob/main/BACKLOG.md)
for open development tasks and limitations.


# how to use 

##todo documentation


# how to use with cmd-line

get cmd-line parameter with

    phyton3 -m smog --help
    
or for a sub-cmd

    phyton3 -m smog *sub-cmd* --help


# additional reference documentation

for expert reading 

- [xmp (wikipedia)](https://en.wikipedia.org/wiki/Extensible_Metadata_Platform)
  - [adobe xmp specfification](https://github.com/adobe/xmp-docs) 
- 


# platform

tested on python3, and linux


# development status

alpha state, use on your own risk!


# installation

`smog` project dependencies: 

- [`SQLAlchemy`](https://www.sqlalchemy.org/)
  - [`alembic`](https://alembic.sqlalchemy.org)
- [`python-xmp-toolkit`](https://python-xmp-toolkit.readthedocs.io/en/latest/)  
  - [`Exempi`](https://libopenraw.freedesktop.org/exempi/)
- [`python-dateutil`](https://dateutil.readthedocs.io/en/latest/)
- 


`smog` itself can be installed with

    phyton3 -m pip install smog
 
 
## initial configuration

after first installation of `smog` run

    smog config -db-init
    
to create an empty database `~/media-db/smog.sb` 


## upgrade from older version

backup your database `~/media-db/smog.sb` and migrate 
the database with  

    smog config -db-migrate


# license

refer to 
`GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007`
[`LICENSE`](https://github.com/kr-g/smog/blob/main/LICENSE.md)


## other licenses

this is not a comprehensive list, 
refer to each project to find more information

- [`SQLAlchemy`](https://github.com/sqlalchemy/sqlalchemy)
  - [`alembic`](https://github.com/sqlalchemy/alembic)
- [`python-xmp-toolkit`](https://github.com/python-xmp-toolkit/python-xmp-toolkit)  
  - [`Exempi`](https://github.com/freedesktop/exempi)
- [`python-dateutil`](https://github.com/python-xmp-toolkit/python-xmp-toolkit)
- 
