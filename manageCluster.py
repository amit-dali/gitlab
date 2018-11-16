import argparse
import gitlab

def getPipeLine(pipelines, ref, status):
	for pipeline in pipelines:
		if(pipeline.ref == ref and pipeline.status == status):
			return pipeline

def getJob(project, pipeline, status, stage):
	jobs = project.jobs.list()
	for job in jobs:
		if(job.stage == stage and (job.status == status or job.status == "success")):
			return job

def gitLabAuthenticate(configFile):
	gl = gitlab.Gitlab.from_config('somewhere', [configFile])
	gl.auth()
	return gl

def setVarValue(project, varName, varValue):
	p_var = project.variables.get(varName)
	p_var.value = varValue
	p_var.save()

def getDestoryJob(project):
	pipelines = project.pipelines.list()
	masterPipeLine = getPipeLine(pipelines, "master", "success")
	job = getJob(project, masterPipeLine, "manual", "dev_destroy")
	return job

def executeJob(job):
	if(job.status == "manual"):
		job.play()
	else:
		job.retry()

def destoryECSCluster(project, ecsClusterName):
	setVarValue(project, 'ECS_CLUSTER_NAME', ecsClusterName)
	destoryJob = getDestoryJob(project)
	executeJob(destoryJob)

def getECSClusterProject(gl):
	return gl.projects.get('aws-ecs')

def creatPipeLine(project, branch):
	return project.pipelines.create({'ref': branch})
			
def createECSCluster(project, ecsClusterName, branch):
	setVarValue(project, 'ECS_CLUSTER_NAME', ecsClusterName)
	setVarValue(project, 'ECS_INSTANCE_PREFIX', ecsClusterName)
	pipeline = creatPipeLine(project, branch)
	print(str(pipeline.id) + " is created to create new ecs cluster with name as " + ecsClusterName)

def actionHandler(gl, args):
	ecsClusterProject = getECSClusterProject(gl)
	if(args.ECS_CLUSTER_ACTION == "create"):
		createECSCluster(ecsClusterProject, args.ECS_CLUSTER_NAME, args.branch)
	elif(args.ECS_CLUSTER_ACTION == "destory"):
		destoryECSCluster(ecsClusterProject, args.ECS_CLUSTER_NAME)
	else:
		print(args.ECS_CLUSTER_ACTION + " is not a valid action")
	
parser = argparse.ArgumentParser(description='Process input values.')
parser.add_argument('ECS_CLUSTER_ACTION', type=str, help='action to perform on ecs cluster')
parser.add_argument('ECS_CLUSTER_NAME', type=str, help='name of ecs cluster')
parser.add_argument('branch', nargs='?', type=str, default="master", help='name of branch')
args = parser.parse_args()
gl = gitLabAuthenticate('python-gitlab.cfg')
actionHandler(gl, args)













