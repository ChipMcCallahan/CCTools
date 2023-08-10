from setuptools import setup, find_packages

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='cc_tools',
    url='https://github.com/ChipMcCallahan/CCTools',
    author='Chip McCallahan',
    author_email='thisischipmccallahan@gmail.com',
    # Needed to actually package something
    packages=['cc_tools'],
    package_data={'cc_tools': [
        'art/8x8/*.png',
        'sets/dat/*.dat',
        'sets/c2m/*/*.c2m',
        'replays/*.tws'
    ]},
    package_dir={'cc_tools': 'src'},
    # Needed for dependencies
    install_requires=[
        'bs4',
        'requests'
    ],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='LICENSE',
    description='Assorted tools for working with and displaying Chip\'s Challenge levels in DAT '
                'or C2M file format.',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
