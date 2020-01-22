from entity_linking.wiki.entity import Entity


def test_entity():
    id = "Q12"
    token = "a"
    instance_of = ["b"]
    subclass_of = ["c"]
    facet_of = ["d"]

    entity: Entity = Entity(id=id, token=token, instance_of=instance_of, subclass_of=subclass_of, facet_of=facet_of)
    assert id == id
    assert entity.token == token
    assert entity.instance_of == instance_of
    assert entity.subclass_of == subclass_of
    assert entity.facet_of == facet_of
