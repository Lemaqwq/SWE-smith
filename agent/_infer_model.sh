#!/bin/bash

sweagent run-batch --config agent/swesmith_infer.yaml \
	--instances.deployment.docker_args=--memory=10g \
	--agent.model.api_base http://0.0.0.0:3000/v1 \
	--random_delay_multiplier=1 \
	--output_dir trajectories/baseline/swe-smith-verified
