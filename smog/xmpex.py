from libxmp import XMPFiles, consts
from libxmp.utils import file_to_dict


def cleanup_xmp(xmpmeta):
    rc = {}
    for ns_k, ns_v in xmpmeta.items():
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


if __name__ == "__main__":
    import os, json

    fnam = "~/Bilder/20220521.jpeg"
    fnam = os.path.expanduser(fnam)

    xmpfile = XMPFiles(file_path=fnam, open_forupdate=False)

    xmpmeta = xmpfile.get_xmp()
    xmpxml = str(xmpmeta)

    # using utility function
    xmp = file_to_dict(fnam)
    # dc = xmp[consts.XMP_NS_XMPMeta]

    xmp_c = cleanup_xmp(xmp)
    tags = xmp_tags(xmp_c)

    print(xmpxml)

    jso = json.dumps(xmp_c, indent=4)
    print(jso)

    for i in tags:
        print(i)
