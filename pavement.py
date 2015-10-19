from cStringIO import StringIO
import ConfigParser
from datetime import date, datetime
import fnmatch
import os
from paver.easy import *
# this pulls in the sphinx target
from paver.doctools import html
import xmlrpclib
import zipfile


options(
    plugin = Bunch(
        name = 'webappbuilder',
        ext_libs = path('webappbuilder/ext-libs'),
        ext_src = path('webappbuilder/ext-src'),
        source_dir = path('webappbuilder'),
        package_dir = path('.'),
        excludes = [
            'metadata.*',           
            '*.pyc',
            'websdk',
            "_websdk"
        ],
        excludes_enterprise = [
            'metadata.*',           
            '*.pyc',
            "_websdk"
        ]
    ),

    # Default Server Params (can be overridden)
    plugin_server = Bunch(
        server = 'qgis.boundlessgeo.com',
        port = 80,
        protocol = 'http',
        end_point = '/RPC2/'
    ),

    sphinx = Bunch(
        docroot = 'doc',
        sourcedir = 'source',
        builddir = 'build'
    )
)



@task
@cmdopts([
    ('clean', 'c', 'clean out dependencies first'),
])
def setup(options):
    '''install dependencies'''
    clean = getattr(options, 'clean', False)
    ext_libs = options.plugin.ext_libs
    ext_src = options.plugin.ext_src
    if clean:
        ext_libs.rmtree()
    ext_libs.makedirs()
    runtime, test = read_requirements()
    os.environ['PYTHONPATH']=ext_libs.abspath()
    for req in runtime + test:
        if req.startswith('-e'):
            # use pip to just process the URL and fetch it in to place
            sh('pip install --no-install --src=%s %s' % (ext_src, req))
            # now change the req to be the location installed to
            # and easy_install will do the rest
            urlspec, req = req.split('#egg=')
            req = ext_src / req
        sh('easy_install -a -d %(ext_libs)s %(dep)s' % {
            'ext_libs' : ext_libs.abspath(),
            'dep' : req
        })
    sdkPath = "./webappbuilder/_websdk"
    if os.path.exists(sdkPath):
        cwd = os.getcwd()
        os.chdir(sdkPath)        
        sh("git pull")
        os.chdir(cwd)
    else:

        sh("git clone https://github.com/boundlessgeo/sdk.git %s" % sdkPath)
    path(os.path.join(sdkPath, "dist", "js", "full.js")).copy2("./webappbuilder/websdk_full/full.js")
    #TODO:copy required files for full version to websdk folder

def read_requirements():
    '''return a list of runtime and list of test requirements'''
    lines = open('requirements.txt').readlines()
    lines = [ l for l in [ l.strip() for l in lines] if l ]
    divider = '# test requirements'
    try:
        idx = lines.index(divider)
    except ValueError:
        raise BuildFailure('expected to find "%s" in requirements.txt' % divider)
    not_comments = lambda s,e: [ l for l in lines[s:e] if l[0] != '#']
    return not_comments(0, idx), not_comments(idx+1, None)


@task
def install(options):
    '''install plugin to qgis'''
    plugin_name = options.plugin.name
    src = path(__file__).dirname() / plugin_name
    dst = path('~').expanduser() / '.qgis2' / 'python' / 'plugins' / plugin_name
    src = src.abspath()
    dst = dst.abspath()       
    dst.rmtree()
    src.copytree(dst)


@task
def package(options):
    '''create package for plugin'''
    package_file = options.plugin.package_dir / ('%s_enterprise.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zip:
        make_zip(zip, options, True)
    package_file = options.plugin.package_dir / ('%s_free.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zip:
        make_zip(zip, options, False)        



def make_zip(zip, options, enterprise):
    metadata_file = options.plugin.source_dir / "metadata.txt"
    cfg = ConfigParser.SafeConfigParser()
    cfg.optionxform = str
    cfg.read(metadata_file)
    base_version = cfg.get('general', 'version')
    head_path = path('.git/HEAD')
    head_ref = head_path.open('rU').readline().strip()[5:]
    ref_file = path(".git/" + head_ref)
    ref = ref_file.open('rU').readline().strip()
    cfg.set("general", "version", "%s-%s-%s" % (base_version, datetime.now().strftime("%Y%m%d"), ref))
    
    buf = StringIO()
    cfg.write(buf)
    zip.writestr("webappbuilder/metadata.txt", buf.getvalue())

    excludes = set(options.plugin.excludes_enterprise) if enterprise else set(options.plugin.excludes)

    src_dir = options.plugin.source_dir
    exclude = lambda p: any([fnmatch.fnmatch(p, e) for e in excludes])
    def filter_excludes(files):
        if not files: return []
        # to prevent descending into dirs, modify the list in place
        for i in xrange(len(files) - 1, -1, -1):
            f = files[i]
            if exclude(f):
                debug('excluding %s' % f)
                files.remove(f)
        return files

    for root, dirs, files in os.walk(src_dir):
        for f in filter_excludes(files):
            relpath = os.path.relpath(root, '.')
            zip.write(path(root) / f, path(relpath) / f)
        filter_excludes(dirs)

