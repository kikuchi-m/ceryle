import pytest
import re

from ceryle.tasks import TaskDependencyError
from ceryle.tasks.resolver import DependencyChain, DependencyResolver, dump_chain


def test_validate_fails_by_cyclic():
    with pytest.raises(TaskDependencyError) as e1:
        resolver = DependencyResolver({
            'a': ['a'],
        })
        resolver.validate()
    assert str(e1.value) == 'cyclic dependency was found: a -> a'

    with pytest.raises(TaskDependencyError) as e2:
        resolver = DependencyResolver({
            'a': ['b'],
            'b': ['a'],
        })
        resolver.validate()
    p2 = 'cyclic dependency was found: (a -> b -> a|b -> a -> b)'
    assert re.match(p2, str(e2.value))

    with pytest.raises(TaskDependencyError) as e3:
        resolver = DependencyResolver({
            'd': ['e'],
            'e': ['f'],
            'f': ['d'],
        })
        resolver.validate()
    p3 = 'cyclic dependency was found: (d -> e -> f -> d|e -> f -> d -> e|f -> d -> e -> f)'
    assert re.match(p3, str(e3.value))

    with pytest.raises(TaskDependencyError) as e4:
        resolver = DependencyResolver({
            'g': ['h'],
            'h': ['i'],
            'i': ['j'],
            'j': ['h'],
        })
        resolver.validate()
    p4 = 'cyclic dependency was found: (h -> i -> j -> h|i -> j -> h -> i|j -> h -> i -> j)'
    assert re.match(p4, str(e4.value))


def test_validate_fails_by_no_depnding_task():
    with pytest.raises(TaskDependencyError) as e:
        resolver = DependencyResolver({
            'a': ['b'],
        })
        resolver.validate()
    assert str(e.value) == 'task b depended by a is not defined'


def test_new_dependency_chain():
    c1 = DependencyChain('c1')

    assert c1.task_name == 'c1'
    assert c1.deps == []


def test_add_dependency_added():
    c1 = DependencyChain('t1')
    c2 = DependencyChain('t2')
    c3 = DependencyChain('t3')

    assert c1.add_dependency(c2) is True
    assert c1.deps == [c2]

    assert c1.add_dependency(c3) is True
    assert c1.deps == [c2, c3]


def test_add_dependency_already_depending():
    c1 = DependencyChain('t1')
    c2 = DependencyChain('t2')
    c3 = DependencyChain('t3')

    assert c1.add_dependency(c2) is True
    assert c1.add_dependency(c2) is False
    assert c1.deps == [c2]

    assert c2.add_dependency(c3) is True
    assert c1.add_dependency(c3) is False
    assert c1.deps == [c2]
    assert c2.deps == [c3]


def test_get_chain():
    c1 = DependencyChain('t1')
    c2 = DependencyChain('t2')
    c3 = DependencyChain('t3')

    assert c1.get_chain(c2) == []
    assert c1.get_chain(c3) == []
    assert c2.get_chain(c3) == []

    c1.add_dependency(c2)

    assert c1.get_chain(c2) == [c2]
    assert c1.get_chain(c3) == []
    assert c2.get_chain(c3) == []

    c2.add_dependency(c3)

    assert c1.get_chain(c2) == [c2]
    assert c1.get_chain(c3) == [c2, c3]
    assert c2.get_chain(c3) == [c3]


def test_dump_chain():

    a11 = DependencyChain('t11')
    a11.add_dependency(DependencyChain('t111'))
    a11.add_dependency(DependencyChain('t112'))

    a12 = DependencyChain('t12')
    a12.add_dependency(DependencyChain('t121'))

    a1 = DependencyChain('t1')
    a1.add_dependency(a11)
    a1.add_dependency(a12)

    res = '''t1
    t11
        t111
        t112
    t12
        t121'''
    assert dump_chain(a1) == res
