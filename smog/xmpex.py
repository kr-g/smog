# xmp specifications from adobe
# https://github.com/adobe/xmp-docs


from libxmp import XMPFiles, consts
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
        # if ns_k in rc:
        #    raise Exception("malformated input")
        rc[ns_k] = ns
    return rc


def xmp_tags(xmp_c):
    rc = []
    for k, v in xmp_c.items():
        rc.extend([(_k, _v) for _k, _v in v.items()])
    return rc
