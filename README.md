[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# smog 

simple media organizer - organize media files 

e.g. a file `20220202_093343.jpg`
is moved into a folder structure like 
`~/media-repo/2022/02/20220202/20220202_093343.jpg`.

if possible xmp/exif metadata is used to determine the date,
otherwise it's extracted from the name (experimental).


# what's new ?

check
[`CHANGELOG`](https://github.com/kr-g/smog/blob/main/CHANGELOG.md)
for latest ongoing, or upcoming news.


# limitations

check 
[`BACKLOG`](https://github.com/kr-g/smog/blob/main/BACKLOG.md)
for open development tasks and limitations.


# how to use

todo: documentation pending

get cmd-line parameter with

    phyton3 -m smog --help


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

smog requires following modules. 

- [`python-xmp-toolkit`](https://github.com/python-xmp-toolkit/python-xmp-toolkit)  
- [`Exempi`](https://libopenraw.freedesktop.org/exempi/)


smog itself can be installed with

    phyton3 -m pip install smog
    

# license

[`LICENSE`](https://github.com/kr-g/smog/blob/main/LICENSE.md)


## other licenses

this is not a comprehensive list, 
refer to each project to find more information

- [`python-xmp-toolkit`](https://github.com/python-xmp-toolkit/python-xmp-toolkit)  
- [`Exempi`](https://libopenraw.freedesktop.org/exempi/)
- 
