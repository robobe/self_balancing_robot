import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

PACKAGE = "self_balancing_robot"
WORLD = "empty.world"
URDF = "robot.urdf.xacro"


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")
    pkg = get_package_share_directory(PACKAGE)

    resources = [os.path.join(pkg, "worlds")]

    resource_env = AppendEnvironmentVariable(
        name="GAZEBO_RESOURCE_PATH", value=":".join(resources)
    )

    models = [os.path.join(pkg, "models")]

    models_env = AppendEnvironmentVariable(
        name="GAZEBO_MODEL_PATH", value=":".join(models)
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gazebo.launch.py"),
        ),
        launch_arguments={"verbose": "true", "world": WORLD}.items(),
    )

    robot_description_path = os.path.join(pkg, "description", URDF)
    doc = xacro.parse(open(robot_description_path))
    xacro.process_doc(doc)

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'use_sim_time': True, 
                'robot_description': doc.toxml()
            }
        ]
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-entity", "demo", "-topic", "robot_description"],
        output="screen",
    )

    ld = LaunchDescription()
    ld.add_action(resource_env)
    ld.add_action(models_env)
    ld.add_action(robot_state_publisher)
    ld.add_action(gazebo)
    ld.add_action(spawn_entity)
    return ld
