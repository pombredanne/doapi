from datetime import datetime
from .base    import Actionable, ResourceWithDroplet, ResourceWithID, \
                        fromISO8601

class Image(Actionable, ResourceWithDroplet, ResourceWithID):
    """
    TODO

    The DigitalOcean API specifies the following fields for domain objects:

    :var id: a unique identifier for the image
    :vartype id: int

    :var name: a human-readable name for the image
    :vartype name: string

    :var type: the type of the image: ``"snapshot"`` or ``"backup"``
    :vartype type: string

    :var distribution: the base Linux distribution used for the image
    :vartype distribution: string

    :var slug: the unique slug identifier for the image (only defined for
        public images)
    :vartype slug: string or ``None``

    :var public: whether the image is public (i.e., available to all accounts)
        or not (i.e., only accessible from your account)
    :vartype public: bool

    :var regions: the slugs of the regions in which the image is available
    :vartype regions: list of strings

    :var min_disk_size: the minimum ``disk`` size required for a droplet to use
        the image
    :vartype min_disk_size: number

    :var created_at: date & time of the image's creation (UTC)
    :vartype created_at: datetime.datetime

    .. attribute:: droplet

       The `Droplet` to which the image belongs.  This attribute is only
       defined for ``Droplet.image`` attributes and the images returned by the
       :meth:`Droplet.fetch_all_backups` and the
       :meth:`Droplet.fetch_all_snapshots` methods.  Images obtained by any
       other means have this attribute set to ``None``.
    """

    def __init__(self, state=None, **extra):
        super(Image, self).__init__(state, **extra)
        if self.get('created_at') is not None and \
                not isinstance(self.created_at, datetime):
            self.created_at = fromISO8601(self.created_at)

    def __str__(self):
        """
        Convert the image to its slug representation.  If the image does not
        have a slug, an ``AttributeError`` is raised.
        """
        if self.get("slug") is not None:
            return self.slug
        else:
            raise AttributeError("%r object has no attribute 'slug'"
                                 % (self.__class__.__name__,))

    @property
    def url(self):
        """ The endpoint for operations on the specific image """
        return self._url('/v2/images/' + str(self.id))

    def fetch(self):
        """
        Fetch & return a new `Image` object representing the image's current
        state

        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the image no longer exists)
        """
        api = self.doapi_manager
        return api._image(api.request(self.url)["image"])

    def update_image(self, name):
        # The `_image` is to avoid conflicts with MutableMapping.update.
        """
        Update (i.e., rename) the image

        :param str name: the new name for the image
        :return: an updated `Image` object
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._image(api.request(self.url, method='PUT',
                                               data={"name": name})["image"])

    def delete(self):
        """
        Delete the image

        :rtype: None
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def transfer(self, region):
        """
        Transfer the image to another region

        :param region: the slug or `Region` object representing the region to
            which to transfer the image
        :type region: string or `Region`
        :return: an `Action` representing the in-progress operation on the
            image
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='transfer', region=region)

    def convert(self):
        """
        Convert the image to a snapshot

        :return: an `Action` representing the in-progress operation on the
            image
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='convert')
