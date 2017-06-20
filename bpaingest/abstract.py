import abc
from .util import make_logger
from urlparse import urlparse


logger = make_logger(__name__)


class ABCBaseMetadata(object):
    __metaclass__ = abc.ABCMeta
    # the package attribute we use to link resources to packages
    resource_linkage = ('bpa_id',)

    @abc.abstractmethod
    def __init__(self, metadata_path):
        pass

    @abc.abstractmethod
    def _get_packages(self):
        """
        return a list of dictionaries representing CKAN packages
        private method, do not call directly.
        """
        pass

    @abc.abstractmethod
    def _get_resources(self):
        """
        return a list of tuples:
          (package_id, legacy_url, resource)
        private method, do not call directly.

        package_id:
          value of attr `resource_linkage` on the corresponding package for
          this resource
        legacy_url: link to download asset from legacy archive
        resource: dictionary representing CKAN resource
        """
        pass


class BaseMetadata(ABCBaseMetadata):

    @classmethod
    def resources_add_format(cls, resources):
        """
        centrally assign formats to resources, based on file extension: no point
        duplicating this function in all the get_resources() implementations.
        if a get_resources() implementation needs to override this, it can just set
        the format key in the resource, and this function will leave the resource
        alone
        """
        extension_map = {
            'JPG': 'JPEG',
            'TGZ': 'TAR',
        }
        for resource_linkage, legacy_url, resource_obj in resources:
            if 'format' in resource_obj:
                continue
            filename = urlparse(legacy_url).path.split('/')[-1]
            if '.' not in filename:
                continue
            extension = filename.rsplit('.', 1)[-1].upper()
            extension = extension_map.get(extension, extension)
            if filename.lower().endswith('.fastq.gz'):
                resource_obj['format'] = 'FASTQ'
            elif filename.lower().endswith('.fasta.gz'):
                resource_obj['format'] = 'FASTA'
            elif extension in ('PNG', 'XLSX', 'XLS', 'PPTX', 'ZIP', 'TAR', 'GZ', 'DOC', 'DOCX', 'PDF', 'CSV', 'JPEG', 'XML', 'BZ2', 'EXE', 'EXF', 'FASTA', 'FASTQ', 'SCAN', 'WIFF'):
                resource_obj['format'] = extension

    def __init__(self):
        self._packages = self._resources = None

    def _get_packages_and_resources(self):
        # ensure that each class can expect to have _get_packages() called first,
        # then _get_resources(), and only once in the entire lifetime of the class.
        if self._packages is None:
            self._packages = self._get_packages()
            self._resources = self._get_resources()
            BaseMetadata.resources_add_format(self._resources)
        return self._packages, self._resources

    def get_packages(self):
        self._get_packages_and_resources()
        return self._packages

    def get_resources(self):
        self._get_packages_and_resources()
        return self._resources
