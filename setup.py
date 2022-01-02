import pathlib
import re
import setuptools


def read_version():
    with open(pathlib.Path(__file__).parent.joinpath('ceryle/__init__.py')) as fp:
        m = re.search(r"^__version__ = '([\d]+(?:\.[\d]+)*((a|b|rc)[\d]+)?(\.post[\d]+)?(\.dev[\d]+)?)'", fp.read())
        if m:
            return m.group(1)
        raise RuntimeError('version not fount')


setuptools.setup(
    name='ceryle',
    description='Task based command runner tool',
    version=read_version(),
    python_requires='>=3.8.0',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ceryle = ceryle.main:entry_point'],
    },
    url='https://github.com/kikuchi-m/ceryle',
    author='Kikuchi Motoki',
    author_email='wildflower.pink0102@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
)
