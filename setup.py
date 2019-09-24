import setuptools


setuptools.setup(
    name='ceryle',
    description='Task based command runner tool',
    version='0.1.1',
    python_requires='>=3.6.5',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ceryle = ceryle.main:entry_point'],
    },
    url='https://github.com/kikuchi-m/ceryle',
    license='MIT',
    clissifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
)