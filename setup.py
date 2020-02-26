import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='SEAMM Dashboard',
        version="0.1.0",
        description='MolSSI SEAMM Dashboard',
        author='Doaa Altarawy',
        author_email='daltarawy@vt.edu',
        url="https://github.com/molssi-seamm/seamm_dashboard.git",
        license='BSD-3C',

        packages=setuptools.find_packages(),

        #install_requires=read_requirements(),

        include_package_data=True,

        extras_require={
            'tests': [
            ],
        },

        tests_require=[],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=True,
    )