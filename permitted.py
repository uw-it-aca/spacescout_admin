""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


class PermittedException(Exception): pass


class Permitted(object):
    def view(self, user, space, spot):
        try:
            return self.edit(user, space, spot)
        except:
            raise PermittedException('User not allowed to view')

    def edit(self, user, space, spot):
        if not (self.is_admin(user)
                or space.manager == user
                or spot.get('manager', '') == user):
            # or user in editors
            raise PermittedException('User not allowed to edit')

    def create(self, user):
        # look for user in blessed groups
        return self.is_admin(user) # in access group

    def is_admin(self, user):
        # look for user in admin group
        return True
