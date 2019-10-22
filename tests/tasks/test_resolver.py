import pytest
import re

from ceryle import TaskGroup, TaskDependencyError, DependencyChain, DependencyResolver
from ceryle.tasks.resolver import dump_chain


def test_validate_fails_by_cyclic():
    with pytest.raises(TaskDependencyError) as e1:
        resolver = DependencyResolver([
            TaskGroup('a', [], 'file1.ceryle', dependencies=['a']),
        ])
        resolver.validate()
    assert str(e1.value) == 'cyclic dependency was found: a -> a'

    with pytest.raises(TaskDependencyError) as e2:
        resolver = DependencyResolver([
            TaskGroup('a', [], 'file1.ceryle', dependencies=['b']),
            TaskGroup('b', [], 'file1.ceryle', dependencies=['a']),
        ])
        resolver.validate()
    p2 = 'cyclic dependency was found: (a -> b -> a|b -> a -> b)'
    assert re.match(p2, str(e2.value))

    with pytest.raises(TaskDependencyError) as e3:
        resolver = DependencyResolver([
            TaskGroup('d', [], 'file1.ceryle', dependencies=['e']),
            TaskGroup('e', [], 'file1.ceryle', dependencies=['f']),
            TaskGroup('f', [], 'file1.ceryle', dependencies=['d']),
        ])
        resolver.validate()
    p3 = 'cyclic dependency was found: (d -> e -> f -> d|e -> f -> d -> e|f -> d -> e -> f)'
    assert re.match(p3, str(e3.value))

    with pytest.raises(TaskDependencyError) as e4:
        resolver = DependencyResolver([
            TaskGroup('g', [], 'file1.ceryle', dependencies=['h']),
            TaskGroup('h', [], 'file1.ceryle', dependencies=['i']),
            TaskGroup('i', [], 'file1.ceryle', dependencies=['j']),
            TaskGroup('j', [], 'file1.ceryle', dependencies=['h']),
        ])
        resolver.validate()
    p4 = 'cyclic dependency was found: (h -> i -> j -> h|i -> j -> h -> i|j -> h -> i -> j)'
    assert re.match(p4, str(e4.value))


def test_validate_fails_by_no_depnding_task():
    with pytest.raises(TaskDependencyError) as e:
        resolver = DependencyResolver([
            TaskGroup('a', [], 'file1.ceryle', dependencies=['b']),
        ])
        resolver.validate()
    assert str(e.value) == 'task b depended by a is not defined'


def test_consstruct_chain_map_no_dependency():
    resolver = DependencyResolver([
        TaskGroup('a', [], 'file1.ceryle'),
        TaskGroup('b', [], 'file1.ceryle'),
    ])
    resolver.validate()
    chain_map = resolver.deps_chain_map()

    assert len(chain_map) == 2
    assert chain_map['a'].deps == []
    assert chain_map['b'].deps == []


def test_construct_chain_map():
    tg_a = TaskGroup('a', [], 'file1.ceryle', dependencies=['b', 'c'])
    tg_b = TaskGroup('b', [], 'file1.ceryle', dependencies=['c'])
    tg_c = TaskGroup('c', [], 'file1.ceryle', dependencies=[])
    resolver = DependencyResolver([tg_a, tg_b, tg_c])
    resolver.validate()
    chain_map = resolver.deps_chain_map()

    assert len(chain_map) == 3

    chain_c = DependencyChain(tg_c)

    chain_b = DependencyChain(tg_b)
    chain_b.add_dependency(chain_c)

    chain_a = DependencyChain(tg_a)
    chain_a.add_dependency(chain_b)

    assert chain_map['a'] == chain_a
    assert chain_map['b'] == chain_b
    assert chain_map['c'] == chain_c


def test_new_dependency_chain():
    tg = TaskGroup('c1', [], 'file1.ceryle')
    c1 = DependencyChain(tg)

    assert c1.root == tg
    assert c1.task_name == 'c1'
    assert c1.deps == []


def test_add_dependency_added():
    c1 = DependencyChain(TaskGroup('t1', [], 'file1.ceryle'))
    c2 = DependencyChain(TaskGroup('t2', [], 'file1.ceryle'))
    c3 = DependencyChain(TaskGroup('t3', [], 'file1.ceryle'))

    assert c1.add_dependency(c2) is True
    assert c1.deps == [c2]

    assert c1.add_dependency(c3) is True
    assert c1.deps == [c2, c3]


def test_add_dependency_already_depending():
    c1 = DependencyChain(TaskGroup('t1', [], 'file1.ceryle'))
    c2 = DependencyChain(TaskGroup('t2', [], 'file1.ceryle'))
    c3 = DependencyChain(TaskGroup('t3', [], 'file1.ceryle'))

    assert c1.add_dependency(c2) is True
    assert c1.add_dependency(c2) is False
    assert c1.deps == [c2]

    assert c2.add_dependency(c3) is True
    assert c1.add_dependency(c3) is False
    assert c1.deps == [c2]
    assert c2.deps == [c3]


def test_add_dependency_of_skip_not_allowed():
    c1 = DependencyChain(TaskGroup('t1', [], 'file1.ceryle'))
    c2 = DependencyChain(TaskGroup('t2', [], 'file1.ceryle', allow_skip=False))
    c3 = DependencyChain(TaskGroup('t3', [], 'file1.ceryle'))

    assert c1.add_dependency(c2) is True
    assert c1.add_dependency(c2) is True
    assert c1.deps == [c2, c2]

    assert c2.add_dependency(c3) is True
    assert c1.add_dependency(c3) is False
    assert c1.deps == [c2, c2]
    assert c2.deps == [c3]

    c4 = DependencyChain(TaskGroup('t4', [], 'file1.ceryle'))
    c5 = DependencyChain(TaskGroup('t5', [], 'file1.ceryle'))
    c6 = DependencyChain(TaskGroup('t6', [], 'file1.ceryle', allow_skip=False))

    assert c4.add_dependency(c5) is True
    assert c5.add_dependency(c6) is True
    assert c4.add_dependency(c6) is True
    assert c4.deps == [c5, c6]
    assert c5.deps == [c6]


def test_get_chain():
    c1 = DependencyChain(TaskGroup('t1', [], 'file1.ceryle'))
    c2 = DependencyChain(TaskGroup('t2', [], 'file1.ceryle'))
    c3 = DependencyChain(TaskGroup('t3', [], 'file1.ceryle'))

    assert c1.get_chain(c2) == []
    assert c1.get_chain(c2, include_self=True) == [c1]
    assert c1.get_chain(c3) == []
    assert c2.get_chain(c3) == []

    c1.add_dependency(c2)

    assert c1.get_chain(c2) == [c2]
    assert c1.get_chain(c2, include_self=True) == [c1, c2]
    assert c1.get_chain(c3) == []
    assert c2.get_chain(c3) == []

    c2.add_dependency(c3)

    assert c1.get_chain(c2) == [c2]
    assert c1.get_chain(c2, include_self=True) == [c1, c2]
    assert c1.get_chain(c3) == [c2, c3]
    assert c1.get_chain(c3, include_self=True) == [c1, c2, c3]
    assert c2.get_chain(c3) == [c3]
    assert c2.get_chain(c3, include_self=True) == [c2, c3]


def test_dependency_chain_equality():
    c1a = DependencyChain(TaskGroup('t1', [], 'file1'))
    c1b = DependencyChain(TaskGroup('t1', [], 'file1'))

    assert c1a == c1b
    assert not c1a != c1b

    c1a.add_dependency(DependencyChain(TaskGroup('t2', [], 'file11')))

    assert not c1a == c1b
    assert c1a != c1b

    c1b.add_dependency(DependencyChain(TaskGroup('t2', [], 'file11.ceryle')))

    assert c1a == c1b
    assert not c1a != c1b

    assert c1a == c1b
    assert not c1a != c1b


def test_dump_chain():

    a11 = DependencyChain(TaskGroup('t11', [], 'file11.ceryle'))
    a11.add_dependency(DependencyChain(TaskGroup('t111', [], 'file1.ceryle')))
    a11.add_dependency(DependencyChain(TaskGroup('t112', [], 'file1.ceryle')))

    a12 = DependencyChain(TaskGroup('t12', [], 'file1.ceryle'))
    a12.add_dependency(DependencyChain(TaskGroup('t121', [], 'file1.ceryle')))

    a1 = DependencyChain(TaskGroup('t1', [], 'file1.ceryle'))
    a1.add_dependency(a11)
    a1.add_dependency(a12)

    res = '''t1
    t11
        t111
        t112
    t12
        t121'''
    assert dump_chain(a1) == res
