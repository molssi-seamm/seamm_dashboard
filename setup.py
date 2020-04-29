import setuptools

with open('requirements_install.txt') as fd:
    requirements = fd.read()

if __name__ == "__main__":
    with open('requirements_install.txt') as fd:
        requirements = fd.read()

    setuptools.setup(
        name='seamm-dashboard',
        version="0.1.0",
        description='MolSSI SEAMM Dashboard',
        author='Jessica Nash',
        author_email='janash@vt.edu',
        url="https://github.com/molssi-seamm/seamm_dashboard.git",
        license='BSD-3C',

        packages=setuptools.find_packages(),

        # Required packages, pulls from pip if needed; do not use for Conda
        # deployment
        install_requires=requirements,

        include_package_data=True,

        extras_require={
            'tests': [
            ],
        },

        tests_require=[],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.8',
        ],
        zip_safe=False,

        entry_points={
            'console_scripts': [
                'seamm_dashboard=seamm_dashboard.results_dashboard.run',
                'seamm-dashboard=seamm_dashboard.results_dashboard.run',
            ],
        }
    )
