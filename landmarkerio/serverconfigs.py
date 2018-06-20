from landmarkerio.server import (lmio_api, add_mode_endpoint, add_lm_endpoints,
                                 add_image_endpoints, add_mesh_endpoints,
                                 add_template_endpoints,
                                 add_collection_endpoints,
                                 add_expression_endpoint)
from landmarkerio.template import CachedFileTemplateAdapter
from landmarkerio.collection import (AllCacheCollectionAdapter,
                                     FileCollectionAdapter)
from landmarkerio.asset import ImageCacheAdapter, MeshCacheAdapter, ModelCacheAdapter

from landmarkerio import Server


def serve_with_cherrypy(app, port=5000, public=False):
    import cherrypy
    # Mount the WSGI callable object (app) on the desired endpoint (e.g.
    # /api/v1)
    cherrypy.tree.graft(app, Server.endpoint)
    update_dict = {
        'server.socket_port': port,
    }
    if public:
        update_dict['server.socket_host'] = '0.0.0.0'

    cherrypy.config.update(update_dict)
    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()


def serve_from_cache(mode, cache_dir, lm_adapter, template_dir=None,
                     upgrade_templates=False, collection_dir=None, dev=False,
                     username=None, password=None):
    r"""

    """

    api, app = lmio_api(dev=dev, username=username, password=password)
    if dev:
        app.debug = True
    # always serve at least images
    add_image_endpoints(api, ImageCacheAdapter(cache_dir))
    if mode == 'image':
        n_dims = 2
    elif mode == 'select':
        n_dims = 2
    elif mode == 'mesh':
        n_dims = 3
        add_mesh_endpoints(api, MeshCacheAdapter(cache_dir))
    elif mode == 'model':
        n_dims = 3
        model_adapter = ModelCacheAdapter(cache_dir)
        add_mesh_endpoints(api, model_adapter)
        add_expression_endpoint(api, model_adapter)
    else:
        raise ValueError("mode must be 'image' or 'mesh' or 'model' or 'select'")
    add_mode_endpoint(api, mode)
    template_adapter = CachedFileTemplateAdapter(
        n_dims, template_dir=template_dir, upgrade_templates=upgrade_templates)
    add_template_endpoints(api, template_adapter)
    add_lm_endpoints(api, lm_adapter, template_adapter)
    if collection_dir is not None:
        collection_adapter = FileCollectionAdapter(collection_dir)
    else:
        collection_adapter = AllCacheCollectionAdapter(cache_dir)
    add_collection_endpoints(api, collection_adapter)
    print(collection_adapter)
    return app
