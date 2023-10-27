#
# Copyright (c) nexB Inc. and others. All rights reserved.
# purldb is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/purldb for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import copy

import logging
import sys

from minecode.management.commands import VerboseCommand
from packagedb.models import Package, Resource

TRACE = False

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


# This is from https://stackoverflow.com/questions/4856882/limiting-memory-use-in-a-large-django-queryset/5188179#5188179
class MemorySavingQuerysetIterator(object):
    def __init__(self,queryset,max_obj_num=1000):
        self._base_queryset = queryset
        self._generator = self._setup()
        self.max_obj_num = max_obj_num

    def _setup(self):
        for i in range(0,self._base_queryset.count(),self.max_obj_num):
            # By making a copy of of the queryset and using that to actually access
            # the objects we ensure that there are only `max_obj_num` objects in
            # memory at any given time
            smaller_queryset = copy.deepcopy(self._base_queryset)[i:i+self.max_obj_num]
            logger.debug('Grabbing next %s objects from DB' % self.max_obj_num)
            for obj in smaller_queryset.iterator():
                yield obj

    def __iter__(self):
        return self._generator

    def next(self):
        return self._generator.next()


class Command(VerboseCommand):
    help = 'Create embedded Package relations between Packages'

    def handle(self, *args, **options):
        packages = Package.objects.all()
        packages_count = packages.count()
        print(f"Checking {packages_count:,} Packages if they are embedded...")
        embedded_packages_count = 0
        for package in MemorySavingQuerysetIterator(packages):
            resources = Resource.objects.filter(sha1=package.sha1)
            embedded = False
            for resource in resources:
                resource_package = resource.package
                if resource_package.embedded_packages.contains(package):
                    continue
                resource_package.embedded_packages.add(package)
                embedded = True
            if embedded:
                embedded_packages_count += 1
        print(f"{embedded_packages_count:,} Packages are embedded in other packages")
