# xmp specifications from adobe
# https://github.com/adobe/xmp-docs


from libxmp import XMPFiles
from libxmp import consts as XMPConst
from libxmp.utils import file_to_dict


def xmp_meta(fnam):
    xmpfile = XMPFiles(file_path=fnam, open_forupdate=False)
    xmpmeta = xmpfile.get_xmp()
    return xmpmeta


def xmp_dict(fnam):
    xmp = file_to_dict(fnam)
    return xmp


def cleanup_xmp_dict(xmp):
    rc = {}
    for ns_k, ns_v in xmp.items():
        ns = {}
        for k, v, _ in ns_v:
            if k in ns:
                raise Exception("malformated input")
            ns[k] = v
        rc[ns_k] = ns
    return rc


def xmp_tags(xmp_c):
    rc = []
    for v in xmp_c.values():
        rc.extend(v.items())
    return rc


def get_tags(fnam):
    xmp = xmp_dict(fnam)
    xmp_c = cleanup_xmp_dict(xmp)
    tags = xmp_tags(xmp_c)
    return tags
