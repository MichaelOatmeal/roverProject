from setuptools import find_packages, setup

package_name = 'mcu_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wayfinder',
    maintainer_email='78619127+MichaelOatmeal@users.noreply.github.com',
    description='TODO: Package description',
    license='GPL-3.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
          'arduino_node = mcu_control.arduino_node:main',
    	    'motor_test = mcu_control.motor_test:main',
          'manual_node = mcu_control.manual_node:main',
        ],
    },
)
