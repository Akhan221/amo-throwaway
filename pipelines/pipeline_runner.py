# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# DISCLAIMER: This code is generated as part of the AutoMLOps output.

"""Sends a PipelineJob to Vertex AI."""

import argparse
import json
import logging
import os
import yaml

from google.cloud import aiplatform

logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(log_level)

def run_pipeline(
    project_id: str,
    pipeline_root: str,
    pipeline_job_location: str,
    pipeline_job_runner_service_account: str,
    parameter_values_path: str,
    pipeline_spec_path: str,
    display_name: str = 'mlops-pipeline-run',
    enable_caching: bool = False):
    """Executes a pipeline run.

    Args:
        project_id: The project_id.
        pipeline_root: GCS location of the pipeline runs metadata.
        pipeline_job_location: The location to run the Pipeline Job in.
        pipeline_job_runner_service_account: Service Account to runner PipelineJobs.
        parameter_values_path: Location of parameter values JSON.
        pipeline_spec_path: Location of the pipeline spec JSON.
        display_name: Name to call the pipeline.
        enable_caching: Should caching be enabled (Boolean)
    """
    with open(parameter_values_path, 'r', encoding='utf-8') as file:
        try:
            pipeline_params = json.load(file)
        except ValueError as exc:
            print(exc)
    logging.debug('Pipeline Parms Configured:')
    logging.debug(pipeline_params)

    # Use local job_spec instead
    if 'gs_pipeline_spec_path' in pipeline_params:
        del pipeline_params['gs_pipeline_spec_path']

    # Set up experiment
    if 'vertex_experiment_tracking_name' in pipeline_params:
        vertex_exp = pipeline_params['vertex_experiment_tracking_name']
        del pipeline_params['vertex_experiment_tracking_name']
    else:
        vertex_exp = None

    aiplatform.init(project=project_id)
    job = aiplatform.PipelineJob(
        display_name = display_name,
        location = pipeline_job_location,
        template_path = pipeline_spec_path,
        pipeline_root = pipeline_root,
        parameter_values = pipeline_params,
        enable_caching = enable_caching)
    logging.debug('AI Platform job built. Submitting...')
    job.submit(
        experiment=vertex_exp,
        service_account=pipeline_job_runner_service_account)
    logging.debug('Job sent!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str,
                        help='The config file for setting default values.')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    run_pipeline(
        project_id=config['gcp']['project_id'],
        pipeline_root=config['pipelines']['pipeline_storage_path'],
        pipeline_job_location=config['gcp']['pipeline_job_location'],
        pipeline_job_runner_service_account=config['gcp']['pipeline_job_runner_service_account'],
        parameter_values_path=config['pipelines']['parameter_values_path'],
        pipeline_spec_path=config['pipelines']['pipeline_job_spec_path'])
