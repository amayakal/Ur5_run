#!/usr/bin/env python
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg

from std_msgs.msg import String

target = None

def set_target(pose):
	global target
	target = pose

def ur5_motion_execute():
  moveit_commander.roscpp_initialize(sys.argv)
  rospy.init_node('ur5_motion_execute',
                  anonymous=True)
  rospy.Subscriber("location", geometry_msgs.msg.Pose, set_target)
  robot = moveit_commander.RobotCommander()
  scene = moveit_commander.PlanningSceneInterface()
  group = moveit_commander.MoveGroupCommander("manipulator")
  display_trajectory_publisher = rospy.Publisher(
                                      '/move_group/display_planned_path',
                                      moveit_msgs.msg.DisplayTrajectory)


  print "============ Initializing..."
  rospy.sleep(10)
  print "============ Reference frame: %s" % group.get_planning_frame()
  grip = group.get_end_effector_link()
  print "============ Reference frame: %s" % group.get_end_effector_link()
  print "============ Printing robot state"
  print robot.get_current_state()
  print "============ Printing robot pose"
  start = group.get_current_pose(grip).pose
  print start


  group.set_goal_position_tolerance(0.1)
  group.set_goal_orientation_tolerance(0.1)
  group.allow_replanning(True)
  rospy.sleep(5)
  fraction = 0.0
  attempts = 0
  maxAttempt = 1000
  waypoints = []
  waypoints.append(group.get_current_pose(grip).pose)
  wpose = group.get_current_pose(grip).pose
  


  wpose.position.z = target.position.z
  waypoints.append(copy.deepcopy(wpose))
  #wpose.position.y = target.position.y
  #waypoints.append(copy.deepcopy(wpose))
  #wpose.position.x = target.position.x
  #waypoints.append(copy.deepcopy(wpose))
  group.set_start_state_to_current_state()
  while fraction < 1.0 and attempts < maxAttempt:
	  (plan3, fraction) = group.compute_cartesian_path(
		                       waypoints,   # waypoints to follow
		                       0.01,        # eef_step
		                       0.0)         # jump_threshold
	  attempts += 1
          print attempts

  print "============ Calculated path..." + str(fraction)
  rospy.sleep(15)
  if fraction == 1.0:
	  #print "executin" + str(plan3)
	  d = 1
	  for x in plan3.joint_trajectory.points:
		  x.velocities = [0.0,0.0,0.0,0.0,0.0,0.0]
		  time_from_start=rospy.Duration(d)
		  d += 2
	  #print "executin2" + str(plan3)
	  group.execute(plan3)

  print group.get_current_pose(grip).pose
  
  rospy.sleep(15)
  
  print "========Going back "
  
  fraction = 0.0
  attempts = 0
  maxAttempt = 1000
  waypoints = []
  waypoints.append(group.get_current_pose(grip).pose)
  
  wpose = group.get_current_pose(grip).pose
  wpose.position = start.position
  waypoints.append(copy.deepcopy(wpose))
  group.set_start_state_to_current_state()
  while fraction < 1.0 and attempts < maxAttempt:
	  (plan3, fraction) = group.compute_cartesian_path(
		                       waypoints,   # waypoints to follow
		                       0.01,        # eef_step
		                       0.0)         # jump_threshold
	  attempts += 1
          print attempts

  print "============ Calculated path..." + str(fraction)
  rospy.sleep(15)
  if fraction == 1.0:
        #print "executin" + str(plan3)
        d = 1
        for x in plan3.joint_trajectory.points:
		x.velocities = [0.0,0.0,0.0,0.0,0.0,0.0]
		time_from_start=rospy.Duration(d)
 		d += 1
        #print "executin2" + str(plan3)
  	group.execute(plan3)


if __name__=='__main__':
  try:
    ur5_motion_execute()
  except rospy.ROSInterruptException:
    pass
