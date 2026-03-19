from setuptools import find_packages, setup

package_name = 'vision_steering'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/shapes.launch.py']),
        ('share/' + package_name + '/worlds', ['worlds/my_shapes.world']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tmeek',
    maintainer_email='tmeek@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'color_detector_node = vision_steering.color_detector_node:main',
        ],
    },
)
