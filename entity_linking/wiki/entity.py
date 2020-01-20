from typing import List


class Entity:
    def __init__(self, id: str, token: str, instance_of: List[str], subclass_of: List[str], facet_of: List[str]):
        self._id = id
        self._token = token
        self._instance_of = instance_of
        self._subclass_of = subclass_of
        self._facet_of = facet_of

    def __eq__(self, other):
        return self.id == other.id and \
               self.token == other.token and \
               self.instance_of == other.instance_of and \
               self.subclass_of == other.subclass_of and \
               self.facet_of == other.facet_of

    def __ne__(self, other):
        return not self == other

    @property
    def id(self) -> str:
        return self._id

    @property
    def token(self) -> str:
        return self._token

    @property
    def instance_of(self) -> List[str]:
        return self._instance_of

    @property
    def subclass_of(self) -> List[str]:
        return self._subclass_of

    @property
    def facet_of(self) -> List[str]:
        return self._facet_of
